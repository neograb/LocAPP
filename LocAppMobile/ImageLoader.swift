import SwiftUI

/// Helper pour charger les images depuis le dossier Images du projet
struct ImageLoader {
    
    /// Charge une image depuis le dossier Images
    /// - Parameters:
    ///   - name: Nom du fichier (avec ou sans extension)
    ///   - subdirectory: Sous-dossier optionnel dans Images (ex: "activites")
    /// - Returns: UIImage si trouvée, nil sinon
    static func loadImage(named name: String, subdirectory: String? = nil) -> UIImage? {
        // Essayer d'abord avec le nom complet (peut inclure l'extension)
        if let image = UIImage(named: name) {
            return image
        }
        
        // Extensions courantes à tester
        let extensions = ["jpeg", "jpg", "png", "heic"]
        
        for ext in extensions {
            let directory = subdirectory != nil ? "Images/\(subdirectory!)" : "Images"
            
            if let path = Bundle.main.path(forResource: name, ofType: ext, inDirectory: directory),
               let image = UIImage(contentsOfFile: path) {
                return image
            }
        }
        
        // Dernier essai : chercher directement dans le bundle
        if let path = Bundle.main.path(forResource: name, ofType: nil),
           let image = UIImage(contentsOfFile: path) {
            return image
        }
        
        return nil
    }
}

/// Vue SwiftUI pour afficher une image depuis le dossier Images avec fallback
struct MazetImage: View {
    let imageName: String
    let subdirectory: String?
    let fallback: AnyView
    
    init(
        _ imageName: String,
        subdirectory: String? = nil,
        @ViewBuilder fallback: () -> some View = { Color.gray }
    ) {
        self.imageName = imageName
        self.subdirectory = subdirectory
        self.fallback = AnyView(fallback())
    }
    
    var body: some View {
        Group {
            if let uiImage = ImageLoader.loadImage(named: imageName, subdirectory: subdirectory) {
                Image(uiImage: uiImage)
                    .resizable()
            } else {
                fallback
            }
        }
    }
}

// MARK: - Remote Image (chargement depuis le serveur)

/// Vue SwiftUI pour charger une image depuis une URL distante
struct RemoteImage: View {
    let url: URL?
    let propertySlug: String?
    let filename: String?
    let isAccessPhoto: Bool
    let fallback: AnyView

    @State private var image: UIImage?
    @State private var isLoading = true

    init(
        url: URL?,
        propertySlug: String? = nil,
        filename: String? = nil,
        isAccessPhoto: Bool = false,
        @ViewBuilder fallback: () -> some View = {
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 0.96, green: 0.87, blue: 0.70),
                        Color(red: 0.55, green: 0.71, blue: 0.67)
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                Image(systemName: "photo")
                    .font(.largeTitle)
                    .foregroundColor(.white.opacity(0.7))
            }
        }
    ) {
        self.url = url
        self.propertySlug = propertySlug
        self.filename = filename
        self.isAccessPhoto = isAccessPhoto
        self.fallback = AnyView(fallback())
    }

    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
            } else if isLoading {
                ZStack {
                    fallback
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                }
            } else {
                fallback
            }
        }
        .task {
            await loadImage()
        }
    }

    private func loadImage() async {
        // 1. Try persistent cache first (downloaded photos)
        if let slug = propertySlug, let name = filename {
            if let cachedImage = PhotoCacheManager.shared.getCachedImage(
                propertySlug: slug,
                filename: name,
                isAccessPhoto: isAccessPhoto
            ) {
                self.image = cachedImage
                isLoading = false
                return
            }
        }

        // Determine URL: use provided url or generate from propertySlug/filename
        let imageURL: URL?
        if let providedURL = url {
            imageURL = providedURL
        } else if let slug = propertySlug, let name = filename {
            imageURL = isAccessPhoto
                ? APIService.accessPhotoURL(propertySlug: slug, filename: name)
                : APIService.photoURL(propertySlug: slug, filename: name)
        } else {
            imageURL = nil
        }

        guard let url = imageURL else {
            isLoading = false
            return
        }

        // 2. Check in-memory cache
        if let cachedImage = ImageCache.shared.get(forKey: url.absoluteString) {
            self.image = cachedImage
            isLoading = false
            return
        }

        // 3. Download from network
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let uiImage = UIImage(data: data) {
                ImageCache.shared.set(uiImage, forKey: url.absoluteString)
                self.image = uiImage
            }
        } catch {
            print("Failed to load image from \(url): \(error)")
        }
        isLoading = false
    }
}

/// Convenience initializer for property photos with cache support
extension RemoteImage {
    init(
        propertySlug: String,
        filename: String,
        isAccessPhoto: Bool = false,
        @ViewBuilder fallback: () -> some View = {
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 0.96, green: 0.87, blue: 0.70),
                        Color(red: 0.55, green: 0.71, blue: 0.67)
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                Image(systemName: "photo")
                    .font(.largeTitle)
                    .foregroundColor(.white.opacity(0.7))
            }
        }
    ) {
        let url = isAccessPhoto
            ? APIService.accessPhotoURL(propertySlug: propertySlug, filename: filename)
            : APIService.photoURL(propertySlug: propertySlug, filename: filename)

        self.init(
            url: url,
            propertySlug: propertySlug,
            filename: filename,
            isAccessPhoto: isAccessPhoto,
            fallback: fallback
        )
    }
}

/// Simple in-memory image cache
class ImageCache {
    static let shared = ImageCache()
    private var cache = NSCache<NSString, UIImage>()

    private init() {
        cache.countLimit = 50
    }

    func get(forKey key: String) -> UIImage? {
        return cache.object(forKey: key as NSString)
    }

    func set(_ image: UIImage, forKey key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
}

// MARK: - Preview
#Preview {
    VStack(spacing: 20) {
        // Exemple d'utilisation basique
        MazetImage("mazet-hero")
            .aspectRatio(contentMode: .fill)
            .frame(height: 200)
            .clipped()

        // Exemple avec sous-dossier
        MazetImage("pont-arc", subdirectory: "activites")
            .aspectRatio(contentMode: .fit)
            .frame(height: 150)

        // Exemple avec fallback personnalisé
        MazetImage("image-inexistante") {
            ZStack {
                Color.blue.opacity(0.2)
                Image(systemName: "photo.fill")
                    .font(.largeTitle)
                    .foregroundColor(.gray)
            }
        }
        .frame(height: 150)
    }
    .padding()
}
