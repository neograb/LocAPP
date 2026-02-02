import SwiftUI

/// Vue pour générer une icône d'app temporaire
/// Utilisez cette vue en Preview, faites une capture d'écran (⌘+S) et utilisez-la comme icône
struct AppIconGenerator: View {
    var body: some View {
        ZStack {
            // Fond dégradé provençal
            LinearGradient(
                colors: [
                    Color(red: 0.90, green: 0.49, blue: 0.13), // Orange
                    Color(red: 0.83, green: 0.33, blue: 0.00)  // Terracotta
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            
            VStack(spacing: 8) {
                // Icône de maison
                Image(systemName: "house.lodge.fill")
                    .font(.system(size: 120))
                    .foregroundStyle(.white)
                    .shadow(color: .black.opacity(0.3), radius: 10, x: 0, y: 5)
                
                // Texte BSA
                Text("BSA")
                    .font(.system(size: 40, weight: .black, design: .rounded))
                    .foregroundStyle(.white)
                    .shadow(color: .black.opacity(0.3), radius: 5, x: 0, y: 2)
            }
        }
        .frame(width: 1024, height: 1024) // Taille standard pour icône iOS
    }
}

/// Vue alternative - style minimaliste
struct AppIconGeneratorMinimal: View {
    var body: some View {
        ZStack {
            // Fond uni
            Color(red: 0.90, green: 0.49, blue: 0.13)
            
            VStack(spacing: 12) {
                // Icône simple
                Image(systemName: "house.fill")
                    .font(.system(size: 140, weight: .semibold))
                    .foregroundStyle(.white)
                
                // Initiales
                Text("M")
                    .font(.system(size: 80, weight: .black, design: .serif))
                    .foregroundStyle(.white)
            }
        }
        .frame(width: 1024, height: 1024)
    }
}

/// Vue alternative - style élégant
struct AppIconGeneratorElegant: View {
    var body: some View {
        ZStack {
            // Fond dégradé doux
            LinearGradient(
                colors: [
                    Color(red: 0.96, green: 0.87, blue: 0.70), // Ocre clair
                    Color(red: 0.90, green: 0.49, blue: 0.13)  // Orange
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            
            VStack(spacing: 16) {
                // Icône de maison stylisée
                Image(systemName: "house.lodge.fill")
                    .font(.system(size: 140, weight: .medium))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.white, Color.white.opacity(0.8)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .shadow(color: .black.opacity(0.2), radius: 20, x: 0, y: 10)
                
                // Nom du mazet
                VStack(spacing: 4) {
                    Text("MAZET")
                        .font(.system(size: 36, weight: .bold, design: .rounded))
                        .foregroundStyle(.white)
                    
                    Rectangle()
                        .fill(.white)
                        .frame(width: 120, height: 3)
                    
                    Text("BSA")
                        .font(.system(size: 28, weight: .semibold, design: .rounded))
                        .foregroundStyle(.white.opacity(0.9))
                }
                .shadow(color: .black.opacity(0.2), radius: 8, x: 0, y: 4)
            }
        }
        .frame(width: 1024, height: 1024)
    }
}

// MARK: - Preview
#Preview("Icône Standard") {
    AppIconGenerator()
}

#Preview("Icône Minimaliste") {
    AppIconGeneratorMinimal()
}

#Preview("Icône Élégante") {
    AppIconGeneratorElegant()
}
