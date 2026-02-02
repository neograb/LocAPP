import SwiftUI

struct AccueilView: View {
    @State private var isAnimated = false
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 30) {
                    
                    // Image d'en-tête - Photo du Mazet
                    ZStack(alignment: .bottomLeading) {
                        // Photo du Mazet (chargée depuis le dossier Images)
                        MazetImage("mazet-hero") {
                            // Fallback : dégradé provençal si l'image n'est pas trouvée
                            LinearGradient(
                                colors: [
                                    Color(red: 0.96, green: 0.87, blue: 0.70), // Ocre clair
                                    Color(red: 0.55, green: 0.71, blue: 0.67)  // Vert provence
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        }
                        .aspectRatio(contentMode: .fill)
                        .frame(height: 280)
                        .clipped()
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        
                        // Overlay pour améliorer la lisibilité du texte
                        LinearGradient(
                            colors: [
                                .clear,
                                .black.opacity(0.6)
                            ],
                            startPoint: .center,
                            endPoint: .bottom
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        
                        // Titre sur l'image
                        Text("Le Mazet de BSA")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundStyle(.white)
                            .shadow(color: .black.opacity(0.5), radius: 10, x: 0, y: 2)
                            .padding()
                    }
                    .padding(.horizontal)
                    .scaleEffect(isAnimated ? 1 : 0.9)
                    .opacity(isAnimated ? 1 : 0)
                    
                    // Message de bienvenue
                    VStack(spacing: 20) {
                        Text("Bienvenue ! 🌿")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundStyle(
                                LinearGradient(
                                    colors: [.orange, .brown],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                        
                        Text("Nous sommes ravis de vous accueillir dans notre Mazet.")
                            .font(.title3)
                            .multilineTextAlignment(.center)
                            .foregroundColor(.secondary)
                        
                        Divider()
                            .padding(.horizontal, 50)
                        
                        // Carte de bienvenue
                        VStack(alignment: .leading, spacing: 15) {
                            HStack {
                                Image(systemName: "sun.max.fill")
                                    .foregroundColor(.orange)
                                    .font(.title2)
                                Text("Profitez de votre séjour")
                                    .font(.headline)
                            }
                            
                            Text("Ce petit coin de paradis provençal est désormais le vôtre le temps de votre séjour. N'hésitez pas à explorer les différentes sections de cette application pour découvrir toutes les informations utiles.")
                                .font(.body)
                                .foregroundColor(.secondary)
                                .lineSpacing(4)
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 15)
                                .fill(Color(.systemBackground))
                                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
                        )
                        .padding(.horizontal)
                    }
                    .offset(y: isAnimated ? 0 : 20)
                    .opacity(isAnimated ? 1 : 0)
                    
                    // Raccourcis rapides
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Accès rapide")
                            .font(.headline)
                            .padding(.horizontal)
                        
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 15) {
                            NavigationLink {
                                WiFiDetailView()
                            } label: {
                                QuickAccessCard(
                                    icon: "wifi",
                                    title: "WiFi",
                                    subtitle: "Code & infos",
                                    color: .blue
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                            
                            NavigationLink {
                                AdresseDetailView()
                            } label: {
                                QuickAccessCard(
                                    icon: "mappin.circle.fill",
                                    title: "Adresse",
                                    subtitle: "GPS & accès",
                                    color: .red
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                            
                            NavigationLink {
                                PhotosView()
                            } label: {
                                QuickAccessCard(
                                    icon: "photo.fill",
                                    title: "Photos",
                                    subtitle: "Galerie",
                                    color: .purple
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                            
                            NavigationLink {
                                UrgencesDetailView()
                            } label: {
                                QuickAccessCard(
                                    icon: "phone.fill",
                                    title: "Urgences",
                                    subtitle: "Numéros utiles",
                                    color: .orange
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                        }
                        .padding(.horizontal)
                    }
                    .offset(y: isAnimated ? 0 : 30)
                    .opacity(isAnimated ? 1 : 0)
                    
                    Spacer(minLength: 30)
                }
                .padding(.top)
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Accueil")
            .navigationBarTitleDisplayMode(.inline)
        }
        .onAppear {
            withAnimation(.easeOut(duration: 0.8)) {
                isAnimated = true
            }
        }
    }
}

// MARK: - Composant réutilisable pour les raccourcis
struct QuickAccessCard: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 10) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)
            
            VStack(spacing: 2) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
        )
    }
}

#Preview {
    AccueilView()
}
