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
