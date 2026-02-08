import SwiftUI
import CoreImage.CIFilterBuiltins
import MapKit

struct InfosPratiquesView: View {
    var body: some View {
        NavigationStack {
            List {
                // Section WiFi
                Section {
                    NavigationLink {
                        WiFiDetailView()
                    } label: {
                        InfoRow(
                            icon: "wifi",
                            iconColor: .blue,
                            title: "WiFi",
                            detail: "QR Code & mot de passe"
                        )
                    }
                } header: {
                    Text("Connexion Internet")
                }
                
                // Section Accès & Parking
                Section {
                    NavigationLink {
                        AdresseDetailView()
                    } label: {
                        InfoRow(
                            icon: "mappin.circle.fill",
                            iconColor: .red,
                            title: "Adresse",
                            detail: "Centre-ville de Bourg-Saint-Andéol"
                        )
                    }
                    
                    NavigationLink {
                        ParkingDetailView()
                    } label: {
                        InfoRow(
                            icon: "car.fill",
                            iconColor: .green,
                            title: "Parking",
                            detail: "Gratuit à 150m"
                        )
                    }
                    
                    NavigationLink {
                        ClesDetailView()
                    } label: {
                        InfoRow(
                            icon: "key.fill",
                            iconColor: .yellow,
                            title: "Clés & Accès",
                            detail: "Arrivée / Départ"
                        )
                    }
                } header: {
                    Text("Accès au Mazet")
                }
                
                // Section Équipements
                Section {
                    InfoRow(
                        icon: "bed.double.fill",
                        iconColor: .purple,
                        title: "Literie",
                        detail: "Lits faits à votre arrivée"
                    )
                    
                    InfoRow(
                        icon: "shower.fill",
                        iconColor: .cyan,
                        title: "Serviettes",
                        detail: "Fournies"
                    )
                    
                    NavigationLink {
                        CuisineDetailView()
                    } label: {
                        InfoRow(
                            icon: "fork.knife",
                            iconColor: .orange,
                            title: "Cuisine",
                            detail: "Équipements disponibles"
                        )
                    }
                } header: {
                    Text("Équipements")
                }
                
                // Section Maison
                Section {
                    NavigationLink {
                        TriSelectifDetailView()
                    } label: {
                        InfoRow(
                            icon: "trash.fill",
                            iconColor: .green,
                            title: "Tri sélectif",
                            detail: "Consignes locales BSA"
                        )
                    }
                    
                    NavigationLink {
                        CheckoutDetailView()
                    } label: {
                        InfoRow(
                            icon: "clock.fill",
                            iconColor: .purple,
                            title: "Check-out",
                            detail: "Procédure de départ"
                        )
                    }
                } header: {
                    Text("Informations pratiques")
                }
                
                // Section Urgences
                Section {
                    Button {
                        if let url = URL(string: "tel://15") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        InfoRow(
                            icon: "cross.case.fill",
                            iconColor: .red,
                            title: "SAMU",
                            detail: "15"
                        )
                    }
                    .tint(.primary)
                    
                    Button {
                        if let url = URL(string: "tel://18") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        InfoRow(
                            icon: "flame.fill",
                            iconColor: .red,
                            title: "Pompiers",
                            detail: "18"
                        )
                    }
                    .tint(.primary)
                    
                    Button {
                        if let url = URL(string: "tel://17") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        InfoRow(
                            icon: "shield.fill",
                            iconColor: .blue,
                            title: "Police",
                            detail: "17"
                        )
                    }
                    .tint(.primary)
                    
                    Button {
                        if let url = URL(string: "tel://112") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        InfoRow(
                            icon: "phone.fill",
                            iconColor: .orange,
                            title: "Urgences Europe",
                            detail: "112"
                        )
                    }
                    .tint(.primary)
                } header: {
                    Text("En cas d'urgence")
                } footer: {
                    Text("Appuyez sur un numéro pour appeler directement")
                }
                
                // Section Services à proximité
                Section {
                    NavigationLink {
                        PharmacieDetailView()
                    } label: {
                        InfoRow(
                            icon: "cross.fill",
                            iconColor: .green,
                            title: "Pharmacie",
                            detail: "Centre-ville BSA"
                        )
                    }
                    
                    NavigationLink {
                        MedecinDetailView()
                    } label: {
                        InfoRow(
                            icon: "stethoscope",
                            iconColor: .blue,
                            title: "Médecin",
                            detail: "Maison de santé BSA"
                        )
                    }
                    
                    NavigationLink {
                        SupermarcheDetailView()
                    } label: {
                        InfoRow(
                            icon: "cart.fill",
                            iconColor: .orange,
                            title: "Supermarché",
                            detail: "Intermarché"
                        )
                    }
                    
                    NavigationLink {
                        BoulangerieDetailView()
                    } label: {
                        InfoRow(
                            icon: "storefront.fill",
                            iconColor: .brown,
                            title: "Boulangerie",
                            detail: "Centre-ville"
                        )
                    }
                } header: {
                    Text("Services à proximité")
                }
            }
            .navigationTitle("Infos Pratiques")
        }
    }
}

// MARK: - Composant ligne d'information
struct InfoRow: View {
    let icon: String
    let iconColor: Color
    let title: String
    let detail: String
    
    var body: some View {
        HStack(spacing: 15) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(iconColor)
                .frame(width: 35)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.body)
                    .fontWeight(.medium)
                
                Text(detail)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding(.vertical, 5)
    }
}

// MARK: - Vue WiFi avec QR Code
struct WiFiDetailView: View {
    @State private var copied = false
    
    // ⚠️ Informations WiFi du Mazet
    let wifiSSID = "Roussel_Bonard_07"
    let wifiPassword = "Solex07700"
    
    var body: some View {
        ScrollView {
            VStack(spacing: 25) {
                
                // En-tête
                VStack(spacing: 10) {
                    Image(systemName: "wifi")
                        .font(.system(size: 50))
                        .foregroundColor(.blue)
                    
                    Text("Connexion WiFi")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Scannez le QR code ou entrez le mot de passe")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 20)
                
                // QR Code
                VStack(spacing: 15) {
                    // Génération du QR Code
                    if let qrImage = generateWiFiQRCode() {
                        Image(uiImage: qrImage)
                            .interpolation(.none)
                            .resizable()
                            .scaledToFit()
                            .frame(width: 200, height: 200)
                            .padding(20)
                            .background(
                                RoundedRectangle(cornerRadius: 20)
                                    .fill(Color.white)
                                    .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
                            )
                    }
                    
                    Text("📱 Scannez avec l'appareil photo")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 25)
                        .fill(Color(.systemGray6))
                )
                .padding(.horizontal)
                
                // Informations de connexion manuelle
                VStack(spacing: 20) {
                    Text("Ou connectez-vous manuellement")
                        .font(.headline)
                    
                    // Nom du réseau
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Nom du réseau (SSID)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        HStack {
                            Image(systemName: "wifi")
                                .foregroundColor(.blue)
                            Text(wifiSSID)
                                .font(.body)
                                .fontWeight(.medium)
                                .fontDesign(.monospaced)
                            
                            Spacer()
                            
                            Button {
                                UIPasteboard.general.string = wifiSSID
                                withAnimation { copied = true }
                                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                    withAnimation { copied = false }
                                }
                            } label: {
                                Image(systemName: "doc.on.doc")
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color(.systemBackground))
                        )
                    }
                    
                    // Mot de passe
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Mot de passe")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        HStack {
                            Image(systemName: "lock.fill")
                                .foregroundColor(.orange)
                            Text(wifiPassword)
                                .font(.title3)
                                .fontWeight(.semibold)
                                .fontDesign(.monospaced)
                            
                            Spacer()
                            
                            Button {
                                UIPasteboard.general.string = wifiPassword
                                withAnimation { copied = true }
                                DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                    withAnimation { copied = false }
                                }
                            } label: {
                                Image(systemName: copied ? "checkmark.circle.fill" : "doc.on.doc")
                                    .foregroundColor(copied ? .green : .blue)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color(.systemBackground))
                        )
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color(.systemGray6))
                )
                .padding(.horizontal)
                
                // Bouton pour ouvrir les réglages WiFi
                Button {
                    if let url = URL(string: "App-Prefs:root=WIFI") {
                        if UIApplication.shared.canOpenURL(url) {
                            UIApplication.shared.open(url)
                        } else if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
                            UIApplication.shared.open(settingsUrl)
                        }
                    }
                } label: {
                    HStack {
                        Image(systemName: "gear")
                        Text("Ouvrir les réglages WiFi")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 15)
                            .fill(Color.blue)
                    )
                }
                .padding(.horizontal)
                
                // Conseil
                VStack(spacing: 10) {
                    Image(systemName: "lightbulb.fill")
                        .foregroundColor(.yellow)
                    
                    Text("Le WiFi couvre l'ensemble du mazet. La box se trouve dans le salon.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                
                Spacer(minLength: 30)
            }
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("WiFi")
        .navigationBarTitleDisplayMode(.inline)
    }
    
    // Génération du QR Code WiFi
    func generateWiFiQRCode() -> UIImage? {
        // Format WiFi standard pour QR code
        let wifiString = "WIFI:T:WPA;S:\(wifiSSID);P:\(wifiPassword);;"
        
        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()
        
        filter.message = Data(wifiString.utf8)
        filter.correctionLevel = "H"
        
        guard let outputImage = filter.outputImage else { return nil }
        
        // Agrandir le QR code
        let transform = CGAffineTransform(scaleX: 10, y: 10)
        let scaledImage = outputImage.transformed(by: transform)
        
        // Convertir en UIImage
        if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
            return UIImage(cgImage: cgImage)
        }
        
        return nil
    }
}

// MARK: - Autres vues de détail

struct AdresseDetailView: View {
    var body: some View {
        List {
            // Section carte
            Section {
                MapSnapshotView(
                    address: "1 Chemin de sainte croix, 07700 Bourg-Saint-Andéol, France"
                )
                .frame(height: 250)
                .cornerRadius(12)
                .listRowInsets(EdgeInsets())
            }
            
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Le Mazet de BSA")
                        .font(.headline)
                    Text("1 Chemin de sainte croix")
                        .font(.body)
                    Text("07700 Bourg-Saint-Andéol")
                        .font(.body)
                    Text("Ardèche, France")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
                
                Button {
                    let address = "1 chemin de Sainte croix, Bourg-Saint-Andéol, Ardèche, France"
                    if let encoded = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                       let url = URL(string: "maps://?address=\(encoded)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Label("Ouvrir dans Plans", systemImage: "map.fill")
                }
            } header: {
                Text("Adresse")
            }
            
            Section {
                Text("Le mazet se situe en plein cœur de Bourg-Saint-Andéol, à proximité immédiate des commerces et restaurants.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("Localisation")
            }
        }
        .navigationTitle("Adresse")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ParkingDetailView: View {
    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 15) {
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("Parking gratuit")
                            .fontWeight(.medium)
                    }
                    
                    Text("Le parking le plus proche se trouve à environ 150 mètres du mazet. Tous les parkings de Bourg-Saint-Andéol sont gratuits.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
            } header: {
                Text("Stationnement")
            }
            
            Section {
                Text("💡 Conseil : En été et les jours de marché (samedi), les places peuvent être plus difficiles à trouver près du centre.")
                    .font(.subheadline)
            }
        }
        .navigationTitle("Parking")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ClesDetailView: View {
    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Label("Arrivée : 16h00", systemImage: "arrow.right.circle.fill")
                        .font(.headline)
                        .foregroundColor(.green)
                    
                    Label("Départ : 10h00", systemImage: "arrow.left.circle.fill")
                        .font(.headline)
                        .foregroundColor(.orange)
                }
                .padding(.vertical, 5)
            } header: {
                Text("Horaires")
            }
            
            Section {
                // Photo de la boîte à clés
                VStack(spacing: 15) {
                    // Photo de la boîte à clés
                    Image("boite-a-cles") // ⚠️ Nom de votre image dans Assets
                        .resizable()
                        .scaledToFill()
                        .frame(height: 200)
                        .clipped()
                        .cornerRadius(12)
                    
                    // Code de la boîte à clés
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Code de la boîte à clés")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        HStack {
                            Image(systemName: "lock.square.fill")
                                .font(.title2)
                                .foregroundColor(.orange)
                            
                            Text("1012") // ⚠️ Remplacez par votre code
                                .font(.system(size: 32, weight: .bold, design: .monospaced))
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            // Bouton pour copier le code
                            Button {
                                UIPasteboard.general.string = "1234"
                            } label: {
                                Image(systemName: "doc.on.doc")
                                    .foregroundColor(.blue)
                            }
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color(.systemGray6))
                        )
                    }
                    
                    Text("La boîte à clés se trouve à l'entrée principale. Utilisez ce code pour l'ouvrir et récupérer les clés de la location.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
            } header: {
                Text("Récupération des clés")
            }
            
            Section {
                VStack(spacing: 15) {
                    // Photo 1 - Accès location
                    Image("entree-location") // ⚠️ Nom de votre image dans Assets
                        .resizable()
                        .scaledToFill()
                        .frame(height: 200)
                        .clipped()
                        .cornerRadius(12)
                    
                    // Photo 2 - Accès location
                    Image("porte-location") // ⚠️ Nom de votre image dans Assets
                        .resizable()
                        .scaledToFill()
                        .frame(height: 200)
                        .clipped()
                        .cornerRadius(12)
                    
                    Text("Après avoir récupéré les clés dans la boîte, utilisez la clé principale pour ouvrir la porte d'entrée. La serrure se trouve à droite de la porte.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
            } header: {
                Text("Accès à la location")
            }
        }
        .navigationTitle("Clés & Accès")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct CuisineDetailView: View {
    var body: some View {
        List {
            Section {
                Label("Réfrigérateur", systemImage: "refrigerator.fill")
                Label("Plaques de cuisson", systemImage: "flame")
                Label("Four", systemImage: "oven.fill")
                Label("Micro-ondes", systemImage: "microwave.fill")
                Label("Cafetière", systemImage: "cup.and.saucer.fill")
                Label("Bouilloire", systemImage: "waterbottle.fill")
                Label("Grille-pain", systemImage: "takeoutbag.and.cup.and.straw.fill")
            } header: {
                Text("Électroménager")
            }
            
            Section {
                Label("Casseroles & poêles", systemImage: "frying.pan.fill")
                Label("Vaisselle complète", systemImage: "fork.knife")
                Label("Verres & tasses", systemImage: "wineglass.fill")
                Label("Couverts", systemImage: "fork.knife")
            } header: {
                Text("Ustensiles")
            }
            
            Section {
                Text("Sel, poivre, huile et vinaigre sont à disposition. Pour vos courses, vous trouverez plusieurs commerces en centre-ville.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("À savoir")
            }
        }
        .navigationTitle("Cuisine")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct TriSelectifDetailView: View {
    var body: some View {
        List {
            Section {
                HStack {
                    Circle()
                        .fill(.yellow)
                        .frame(width: 30, height: 30)
                    VStack(alignment: .leading) {
                        Text("Bac jaune")
                            .fontWeight(.medium)
                        Text("Emballages, plastiques, cartons")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                HStack {
                    Circle()
                        .fill(.green)
                        .frame(width: 30, height: 30)
                    VStack(alignment: .leading) {
                        Text("Bac vert")
                            .fontWeight(.medium)
                        Text("Verre (bouteilles, pots)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                HStack {
                    Circle()
                        .fill(.gray)
                        .frame(width: 30, height: 30)
                    VStack(alignment: .leading) {
                        Text("Bac gris/noir")
                            .fontWeight(.medium)
                        Text("Ordures ménagères")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            } header: {
                Text("Les poubelles")
            }
            
            Section {
                Text("Les conteneurs de tri se trouvent à proximité du mazet. Merci de bien trier vos déchets pour préserver notre belle Ardèche ! 🌿")
                    .font(.subheadline)
            }
        }
        .navigationTitle("Tri sélectif")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct CheckoutDetailView: View {
    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 15) {
                    Label("Départ avant 10h00", systemImage: "clock.fill")
                        .font(.headline)
                        .foregroundColor(.orange)
                }
            } header: {
                Text("Horaire")
            }
            
            Section {
                Label("Faire la vaisselle", systemImage: "dishwasher.fill")
                Label("Vider le réfrigérateur", systemImage: "refrigerator.fill")
                Label("Sortir les poubelles", systemImage: "trash.fill")
                Label("Fermer les fenêtres", systemImage: "window.ceiling.closed")
                Label("Éteindre les lumières", systemImage: "lightbulb.fill")
                Label("Remettre les clés", systemImage: "key.fill")
            } header: {
                Text("Avant de partir")
            }
            
            Section {
                Text("Merci de laisser le mazet dans l'état où vous l'avez trouvé. Un ménage de fin de séjour est prévu, mais votre aide est appréciée ! 🙏")
                    .font(.subheadline)
            }
        }
        .navigationTitle("Check-out")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Vues Services à proximité

struct PharmacieDetailView: View {
    var body: some View {
        List {
            // Section carte
            Section {
                MapSnapshotView(
                    address: "Pharmacie du Rhône, Place du Champ de Mars, 07700 Bourg-Saint-Andéol, France"
                )
                .frame(height: 250)
                .cornerRadius(12)
                .listRowInsets(EdgeInsets())
            }
            
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Pharmacie du Rhône")
                        .font(.headline)
                    Text("Place du Champ de Mars")
                        .font(.body)
                    Text("07700 Bourg-Saint-Andéol")
                        .font(.body)
                    Text("France")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
                
                Button {
                    let address = "Pharmacie du Rhône, Place du Champ de Mars, Bourg-Saint-Andéol"
                    if let encoded = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                       let url = URL(string: "maps://?address=\(encoded)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Label("Ouvrir dans Plans", systemImage: "map.fill")
                }
            } header: {
                Text("Adresse")
            }
            
            Section {
                Text("Pharmacie située en plein centre-ville, à proximité immédiate du mazet.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("Informations")
            }
        }
        .navigationTitle("Pharmacie")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct MedecinDetailView: View {
    var body: some View {
        List {
            // Section carte
            Section {
                MapSnapshotView(
                    address: "Maison de Santé, Avenue Paul Lafargue, 07700 Bourg-Saint-Andéol, France"
                )
                .frame(height: 250)
                .cornerRadius(12)
                .listRowInsets(EdgeInsets())
            }
            
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Maison de Santé")
                        .font(.headline)
                    Text("Avenue Paul Lafargue")
                        .font(.body)
                    Text("07700 Bourg-Saint-Andéol")
                        .font(.body)
                    Text("France")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
                
                Button {
                    let address = "Maison de Santé, Avenue Paul Lafargue, Bourg-Saint-Andéol"
                    if let encoded = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                       let url = URL(string: "maps://?address=\(encoded)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Label("Ouvrir dans Plans", systemImage: "map.fill")
                }
            } header: {
                Text("Adresse")
            }
            
            Section {
                Text("Maison de santé pluridisciplinaire regroupant médecins généralistes et spécialistes.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("Informations")
            }
        }
        .navigationTitle("Médecin")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct SupermarcheDetailView: View {
    var body: some View {
        List {
            // Section carte
            Section {
                MapSnapshotView(
                    address: "Intermarché SUPER, ZAC des Faysses, 07700 Bourg-Saint-Andéol, France"
                )
                .frame(height: 250)
                .cornerRadius(12)
                .listRowInsets(EdgeInsets())
            }
            
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Intermarché SUPER")
                        .font(.headline)
                    Text("ZAC des Faysses")
                        .font(.body)
                    Text("07700 Bourg-Saint-Andéol")
                        .font(.body)
                    Text("France")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
                
                Button {
                    let address = "Intermarché SUPER, ZAC des Faysses, Bourg-Saint-Andéol"
                    if let encoded = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                       let url = URL(string: "maps://?address=\(encoded)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Label("Ouvrir dans Plans", systemImage: "map.fill")
                }
                
                // Bouton pour appeler
                Button {
                    if let url = URL(string: "tel://0475545454") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Label("Appeler le magasin", systemImage: "phone.fill")
                }
            } header: {
                Text("Adresse & Contact")
            }
            
            Section {
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Image(systemName: "clock.fill")
                            .foregroundColor(.blue)
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Lundi - Samedi")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            Text("8h30 - 19h30")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    HStack {
                        Image(systemName: "clock.fill")
                            .foregroundColor(.blue)
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Dimanche")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            Text("9h00 - 13h00")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .padding(.vertical, 5)
            } header: {
                Text("Horaires")
            }
            
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Label("Alimentation générale", systemImage: "cart.fill")
                    Label("Boucherie - Charcuterie", systemImage: "basket.fill")
                    Label("Fruits & Légumes", systemImage: "leaf.fill")
                    Label("Boulangerie", systemImage: "birthday.cake.fill")
                    Label("Produits frais", systemImage: "refrigerator.fill")
                    Label("Parking gratuit", systemImage: "parkingsign.circle.fill")
                    Label("Station essence", systemImage: "fuelpump.fill")
                }
                .font(.subheadline)
                .foregroundColor(.secondary)
            } header: {
                Text("Services disponibles")
            }
            
            Section {
                Text("Supermarché complet situé dans la zone commerciale des Faysses, à environ 2 km du centre-ville. Idéal pour faire vos courses avec un large choix de produits.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("Informations")
            }
        }
        .navigationTitle("Supermarché")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct BoulangerieDetailView: View {
    var body: some View {
        List {
            // Section carte
            Section {
                MapSnapshotView(
                    address: "Boulangerie Pâtisserie, Place du Champ de Mars, 07700 Bourg-Saint-Andéol, France"
                )
                .frame(height: 250)
                .cornerRadius(12)
                .listRowInsets(EdgeInsets())
            }
            
            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Boulangerie Pâtisserie")
                        .font(.headline)
                    Text("Place du Champ de Mars")
                        .font(.body)
                    Text("07700 Bourg-Saint-Andéol")
                        .font(.body)
                    Text("France")
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 5)
                
                Button {
                    let address = "Boulangerie, Place du Champ de Mars, Bourg-Saint-Andéol"
                    if let encoded = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                       let url = URL(string: "maps://?address=\(encoded)") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    Label("Ouvrir dans Plans", systemImage: "map.fill")
                }
            } header: {
                Text("Adresse")
            }
            
            Section {
                Text("Boulangerie artisanale proposant pain frais, viennoiseries et pâtisseries. Plusieurs boulangeries sont disponibles dans le centre-ville.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } header: {
                Text("Informations")
            }
        }
        .navigationTitle("Boulangerie")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct UrgencesDetailView: View {
    var body: some View {
        List {
            Section {
                Button {
                    if let url = URL(string: "tel://15") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    InfoRow(
                        icon: "cross.case.fill",
                        iconColor: .red,
                        title: "SAMU",
                        detail: "15"
                    )
                }
                .tint(.primary)
                
                Button {
                    if let url = URL(string: "tel://18") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    InfoRow(
                        icon: "flame.fill",
                        iconColor: .red,
                        title: "Pompiers",
                        detail: "18"
                    )
                }
                .tint(.primary)
                
                Button {
                    if let url = URL(string: "tel://17") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    InfoRow(
                        icon: "shield.fill",
                        iconColor: .blue,
                        title: "Police",
                        detail: "17"
                    )
                }
                .tint(.primary)
                
                Button {
                    if let url = URL(string: "tel://112") {
                        UIApplication.shared.open(url)
                    }
                } label: {
                    InfoRow(
                        icon: "phone.fill",
                        iconColor: .orange,
                        title: "Urgences Europe",
                        detail: "112"
                    )
                }
                .tint(.primary)
            } header: {
                Text("En cas d'urgence")
            } footer: {
                Text("Appuyez sur un numéro pour appeler directement")
            }
            
            Section {
                InfoRow(
                    icon: "cross.fill",
                    iconColor: .green,
                    title: "Pharmacie",
                    detail: "Centre-ville BSA"
                )
                
                InfoRow(
                    icon: "stethoscope",
                    iconColor: .blue,
                    title: "Médecin",
                    detail: "Maison de santé BSA"
                )
            } header: {
                Text("Services médicaux à proximité")
            }
        }
        .navigationTitle("Urgences")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - MapSnapshotView

struct MapSnapshotView: View {
    let address: String
    @State private var snapshotImage: UIImage?
    @State private var isLoading = true
    
    var body: some View {
        ZStack {
            if let image = snapshotImage {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } else if isLoading {
                ZStack {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                    
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle())
                }
            } else {
                // Fallback en cas d'erreur
                ZStack {
                    Rectangle()
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color(red: 0.96, green: 0.87, blue: 0.70),
                                    Color(red: 0.55, green: 0.71, blue: 0.67)
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    VStack {
                        Image(systemName: "map.fill")
                            .font(.largeTitle)
                            .foregroundColor(.white.opacity(0.7))
                        Text("Carte non disponible")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.9))
                    }
                }
            }
        }
        .task {
            await generateSnapshot()
        }
    }
    
    func generateSnapshot() async {
        do {
            // Utiliser MKLocalSearch pour géocoder l'adresse
            let searchRequest = MKLocalSearch.Request()
            searchRequest.naturalLanguageQuery = address
            
            let search = MKLocalSearch(request: searchRequest)
            let response = try await search.start()
            
            guard let mapItem = response.mapItems.first else {
                isLoading = false
                return
            }
            
            let coordinate = mapItem.location.coordinate
            
            let options = MKMapSnapshotter.Options()
            options.region = MKCoordinateRegion(
                center: coordinate,
                span: MKCoordinateSpan(latitudeDelta: 0.01, longitudeDelta: 0.01)
            )
            options.size = CGSize(width: 400, height: 300)
            // Utiliser un scale par défaut de 2.0 pour la rétina
            options.scale = 2.0
            
            let snapshotter = MKMapSnapshotter(options: options)
            let snapshot = try await snapshotter.start()
            
            // Ajouter un pin sur la carte
            let image = UIGraphicsImageRenderer(size: options.size).image { context in
                snapshot.image.draw(at: .zero)
                
                let pinPoint = snapshot.point(for: coordinate)
                
                // Ombre du pin
                context.cgContext.setShadow(
                    offset: CGSize(width: 0, height: 2),
                    blur: 4,
                    color: UIColor.black.withAlphaComponent(0.3).cgColor
                )
                
                // Dessiner le pin rouge
                UIColor.systemRed.setFill()
                let pinPath = UIBezierPath()
                pinPath.move(to: CGPoint(x: pinPoint.x, y: pinPoint.y))
                pinPath.addLine(to: CGPoint(x: pinPoint.x - 10, y: pinPoint.y - 25))
                pinPath.addArc(
                    withCenter: CGPoint(x: pinPoint.x, y: pinPoint.y - 25),
                    radius: 10,
                    startAngle: .pi,
                    endAngle: 0,
                    clockwise: true
                )
                pinPath.addLine(to: CGPoint(x: pinPoint.x, y: pinPoint.y))
                pinPath.fill()
                
                // Cercle blanc au centre du pin
                UIColor.white.setFill()
                let innerCircle = UIBezierPath(
                    arcCenter: CGPoint(x: pinPoint.x, y: pinPoint.y - 25),
                    radius: 4,
                    startAngle: 0,
                    endAngle: .pi * 2,
                    clockwise: true
                )
                innerCircle.fill()
            }
            
            snapshotImage = image
            isLoading = false
            
        } catch {
            print("Erreur lors de la génération de la carte : \(error)")
            isLoading = false
        }
    }
}

#Preview {
    InfosPratiquesView()
}
