import SwiftUI

struct PhotosView: View {
    @State private var selectedPhoto: String?
    @State private var showingFullScreen = false
    
    // Liste des photos du Mazet (à personnaliser avec vos vraies photos)
    let photos = [
        "mazet-hero",
        "mazet-salon",
        "mazet-cuisine",
        "mazet-chambre",
        "mazet-salle-de-bain",
        "mazet-terrasse"
    ]
    
    let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10)
    ]
    
    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: columns, spacing: 10) {
                    ForEach(photos, id: \.self) { photo in
                        Button {
                            selectedPhoto = photo
                            showingFullScreen = true
                        } label: {
                            MazetImage(photo) {
                                // Fallback : un dégradé avec le nom de la photo
                                ZStack {
                                    LinearGradient(
                                        colors: [
                                            Color(red: 0.96, green: 0.87, blue: 0.70),
                                            Color(red: 0.55, green: 0.71, blue: 0.67)
                                        ],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                    
                                    VStack {
                                        Image(systemName: "photo")
                                            .font(.largeTitle)
                                            .foregroundColor(.white.opacity(0.7))
                                        Text(photoTitle(for: photo))
                                            .font(.caption)
                                            .foregroundColor(.white.opacity(0.9))
                                            .multilineTextAlignment(.center)
                                            .padding(.horizontal, 5)
                                    }
                                }
                            }
                            .aspectRatio(1, contentMode: .fill)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                            .clipped()
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Photos")
            .navigationBarTitleDisplayMode(.inline)
            .sheet(isPresented: $showingFullScreen) {
                if let selectedPhoto = selectedPhoto {
                    FullScreenPhotoView(photoName: selectedPhoto)
                }
            }
        }
    }
    
    // Helper pour convertir le nom de fichier en titre lisible
    func photoTitle(for photoName: String) -> String {
        let title = photoName.replacingOccurrences(of: "mazet-", with: "")
            .replacingOccurrences(of: "-", with: " ")
        return title.prefix(1).uppercased() + title.dropFirst()
    }
}

// MARK: - Vue plein écran pour une photo

struct FullScreenPhotoView: View {
    @Environment(\.dismiss) var dismiss
    let photoName: String
    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()
                
                MazetImage(photoName) {
                    // Fallback
                    ZStack {
                        LinearGradient(
                            colors: [
                                Color(red: 0.96, green: 0.87, blue: 0.70),
                                Color(red: 0.55, green: 0.71, blue: 0.67)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        
                        VStack {
                            Image(systemName: "photo")
                                .font(.system(size: 80))
                                .foregroundColor(.white.opacity(0.7))
                            Text(photoTitle(for: photoName))
                                .font(.title2)
                                .foregroundColor(.white.opacity(0.9))
                                .multilineTextAlignment(.center)
                                .padding()
                        }
                    }
                }
                .aspectRatio(contentMode: .fit)
                .scaleEffect(scale)
                .gesture(
                    MagnificationGesture()
                        .onChanged { value in
                            scale = lastScale * value
                        }
                        .onEnded { _ in
                            lastScale = scale
                            // Limiter le zoom
                            if scale < 1 {
                                withAnimation {
                                    scale = 1
                                    lastScale = 1
                                }
                            } else if scale > 4 {
                                withAnimation {
                                    scale = 4
                                    lastScale = 4
                                }
                            }
                        }
                )
                .onTapGesture(count: 2) {
                    // Double tap pour réinitialiser le zoom
                    withAnimation {
                        scale = 1
                        lastScale = 1
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Fermer") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
            }
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbarBackground(Color.black.opacity(0.8), for: .navigationBar)
        }
    }
    
    func photoTitle(for photoName: String) -> String {
        let title = photoName.replacingOccurrences(of: "mazet-", with: "")
            .replacingOccurrences(of: "-", with: " ")
        return title.prefix(1).uppercased() + title.dropFirst()
    }
}

#Preview {
    PhotosView()
}
