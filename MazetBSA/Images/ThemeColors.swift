import SwiftUI

/// Thème de couleurs pour l'application Mazet BSA
extension Color {
    
    // MARK: - Couleurs principales du Mazet
    
    /// Orange terre cuite provençal (couleur d'accent principale)
    static let mazetAccent = Color(red: 0.90, green: 0.49, blue: 0.13) // #E67E22
    
    /// Ocre clair provençal
    static let mazetOcre = Color(red: 0.96, green: 0.87, blue: 0.70)
    
    /// Vert provence
    static let mazetVert = Color(red: 0.55, green: 0.71, blue: 0.67)
    
    /// Terracotta foncé
    static let mazetTerracotta = Color(red: 0.83, green: 0.33, blue: 0.00) // #D35400
    
    // MARK: - Dégradés thématiques
    
    /// Dégradé provençal (ocre vers vert)
    static let mazetGradient = LinearGradient(
        colors: [mazetOcre, mazetVert],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
    
    /// Dégradé sunset (orange vers terracotta)
    static let mazetSunset = LinearGradient(
        colors: [mazetAccent, mazetTerracotta],
        startPoint: .leading,
        endPoint: .trailing
    )
}

// MARK: - Preview
#Preview {
    VStack(spacing: 20) {
        Text("Couleurs du Mazet")
            .font(.title)
            .fontWeight(.bold)
        
        // Couleurs principales
        HStack(spacing: 15) {
            VStack {
                Circle()
                    .fill(Color.mazetAccent)
                    .frame(width: 60, height: 60)
                Text("Accent")
                    .font(.caption)
            }
            
            VStack {
                Circle()
                    .fill(Color.mazetOcre)
                    .frame(width: 60, height: 60)
                Text("Ocre")
                    .font(.caption)
            }
            
            VStack {
                Circle()
                    .fill(Color.mazetVert)
                    .frame(width: 60, height: 60)
                Text("Vert")
                    .font(.caption)
            }
            
            VStack {
                Circle()
                    .fill(Color.mazetTerracotta)
                    .frame(width: 60, height: 60)
                Text("Terracotta")
                    .font(.caption)
            }
        }
        
        Divider()
        
        // Dégradés
        VStack(spacing: 10) {
            Rectangle()
                .fill(Color.mazetGradient)
                .frame(height: 100)
                .cornerRadius(12)
                .overlay(
                    Text("Dégradé Provençal")
                        .foregroundColor(.white)
                        .fontWeight(.bold)
                )
            
            Rectangle()
                .fill(Color.mazetSunset)
                .frame(height: 100)
                .cornerRadius(12)
                .overlay(
                    Text("Dégradé Sunset")
                        .foregroundColor(.white)
                        .fontWeight(.bold)
                )
        }
    }
    .padding()
}
