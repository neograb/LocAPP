import SwiftUI

struct ContactView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 25) {
                    
                    // Photo / Avatar de l'hôte
                    VStack(spacing: 15) {
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [.orange.opacity(0.3), .yellow.opacity(0.3)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 120, height: 120)
                            
                            Image("host-photo")
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: 120, height: 120)
                                .clipShape(Circle())
                        }
                        
                        Text("Votre hôte")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text("À votre service pour un séjour parfait en Ardèche")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, 20)
                    
                    // Boutons de contact
                    VStack(spacing: 15) {
                        
                        // Appeler
                        ContactButton(
                            icon: "phone.fill",
                            title: "Appeler",
                            subtitle: "06 88 46 16 07", // À personnaliser
                            color: .green
                        ) {
                            // Action : ouvrir l'app téléphone
                            if let url = URL(string: "tel://+33688461607") { // À personnaliser
                                UIApplication.shared.open(url)
                            }
                        }
                        
                        // SMS
                        ContactButton(
                            icon: "message.fill",
                            title: "Envoyer un SMS",
                            subtitle: "Réponse rapide",
                            color: .blue
                        ) {
                            // Action : ouvrir Messages
                            if let url = URL(string: "sms://+33688461607") { // À personnaliser
                                UIApplication.shared.open(url)
                            }
                        }
                        
                        // WhatsApp
                        ContactButton(
                            icon: "bubble.left.and.bubble.right.fill",
                            title: "WhatsApp",
                            subtitle: "Disponible 7j/7",
                            color: Color(red: 0.2, green: 0.7, blue: 0.3)
                        ) {
                            // Action : ouvrir WhatsApp
                            if let url = URL(string: "https://wa.me/33688461607") { // À personnaliser
                                UIApplication.shared.open(url)
                            }
                        }
                        
                        // Email
                        ContactButton(
                            icon: "envelope.fill",
                            title: "Email",
                            subtitle: "solex07700@gmail.com", // À personnaliser
                            color: .orange
                        ) {
                            // Action : ouvrir Mail
                            if let url = URL(string: "mailto:solex07700@gmail.com") { // À personnaliser
                                UIApplication.shared.open(url)
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // Messagerie Airbnb
                    VStack(spacing: 15) {
                        Divider()
                            .padding(.horizontal, 50)
                        
                        VStack(spacing: 10) {
                            HStack {
                                Image(systemName: "house.fill")
                                    .foregroundColor(.red)
                                Text("Messagerie Airbnb")
                                    .fontWeight(.medium)
                            }
                            .font(.headline)
                            
                            Text("Vous pouvez aussi nous contacter via la messagerie de l'application Airbnb")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                            
                            Button {
                                // Ouvrir Airbnb
                                if let url = URL(string: "airbnb://") {
                                    if UIApplication.shared.canOpenURL(url) {
                                        UIApplication.shared.open(url)
                                    } else if let webUrl = URL(string: "https://www.airbnb.fr/rooms/1057934025843677755") {
                                        UIApplication.shared.open(webUrl)
                                    }
                                }
                            } label: {
                                Text("Ouvrir Airbnb")
                                    .font(.subheadline)
                                    .fontWeight(.medium)
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 25)
                                    .padding(.vertical, 12)
                                    .background(
                                        RoundedRectangle(cornerRadius: 25)
                                            .fill(Color.red)
                                    )
                            }
                        }
                        .padding()
                    }
                    
                    // Conseils de contact
                    VStack(spacing: 10) {
                        Image(systemName: "lightbulb.fill")
                            .font(.title2)
                            .foregroundColor(.yellow)
                        
                        Text("Conseils")
                            .font(.headline)
                        
                        VStack(alignment: .leading, spacing: 8) {
                            HStack(alignment: .top) {
                                Text("•")
                                Text("Pour les questions non urgentes, privilégiez le SMS ou WhatsApp")
                            }
                            HStack(alignment: .top) {
                                Text("•")
                                Text("Pour les urgences, n'hésitez pas à appeler directement")
                            }
                            HStack(alignment: .top) {
                                Text("•")
                                Text("Je réponds généralement dans l'heure")
                            }
                        }
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(
                        RoundedRectangle(cornerRadius: 15)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
                    )
                    .padding(.horizontal)
                    
                    // Numéros d'urgence locaux
                    VStack(spacing: 15) {
                        Text("Numéros utiles en Ardèche")
                            .font(.headline)
                        
                        VStack(spacing: 10) {
                            EmergencyRow(title: "SAMU", number: "15", color: .red)
                            EmergencyRow(title: "Pompiers", number: "18", color: .red)
                            EmergencyRow(title: "Police", number: "17", color: .blue)
                            EmergencyRow(title: "Urgences Europe", number: "112", color: .orange)
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(
                        RoundedRectangle(cornerRadius: 15)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
                    )
                    .padding(.horizontal)
                    
                    Spacer(minLength: 30)
                }
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Contact")
        }
    }
}

// MARK: - Bouton de contact réutilisable
struct ContactButton: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 15) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(color)
                    )
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 15)
                    .fill(Color(.systemBackground))
                    .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Ligne numéro d'urgence
struct EmergencyRow: View {
    let title: String
    let number: String
    let color: Color
    
    var body: some View {
        Button {
            if let url = URL(string: "tel://\(number)") {
                UIApplication.shared.open(url)
            }
        } label: {
            HStack {
                Text(title)
                    .foregroundColor(.primary)
                Spacer()
                Text(number)
                    .fontWeight(.bold)
                    .foregroundColor(color)
                Image(systemName: "phone.fill")
                    .foregroundColor(color)
                    .font(.caption)
            }
            .padding(.vertical, 5)
        }
    }
}

#Preview {
    ContactView()
}
