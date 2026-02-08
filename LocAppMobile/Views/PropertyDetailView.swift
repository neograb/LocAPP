import SwiftUI
import CoreImage.CIFilterBuiltins
import MapKit

struct PropertyDetailView: View {
    let reservation: Reservation

    @State private var propertyData: PropertyData?
    @State private var isLoading = true
    @State private var error: String?

    var body: some View {
        Group {
            if isLoading {
                ProgressView("Chargement...")
            } else if let data = propertyData {
                // Use data.property.slug to ensure photos match the loaded property data
                PropertyContentView(data: data, propertySlug: data.property.slug)
            } else if let error = error {
                VStack(spacing: 15) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundColor(.orange)
                    Text(error)
                        .foregroundColor(.secondary)
                    Button("Réessayer") {
                        Task {
                            await loadData()
                        }
                    }
                }
            }
        }
        .navigationTitle(reservation.propertyName)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.hidden, for: .tabBar)
        .task {
            await loadData()
        }
    }

    private func loadData() async {
        isLoading = true
        error = nil

        do {
            print("📱 Loading property data for reservation \(reservation.id)")
            propertyData = try await APIService.shared.getPropertyData(reservationId: reservation.id)
            print("✅ Property data loaded successfully")
        } catch let apiError as APIError {
            print("❌ API Error: \(apiError.errorDescription ?? "unknown")")
            error = apiError.errorDescription
        } catch {
            print("❌ Error: \(error)")
            self.error = "Erreur de chargement"
        }
        isLoading = false
    }
}

// MARK: - Property Content View

struct PropertyContentView: View {
    let data: PropertyData
    let propertySlug: String

    var body: some View {
        TabView {
            // Accueil
            PropertyAccueilView(data: data, propertySlug: propertySlug)
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("Accueil")
                }

            // Infos Pratiques
            PropertyInfosView(data: data, propertySlug: propertySlug)
                .tabItem {
                    Image(systemName: "info.circle.fill")
                    Text("Infos")
                }

            // Activités
            PropertyActivitesView(data: data)
                .tabItem {
                    Image(systemName: "star.fill")
                    Text("Activités")
                }

            // Contact
            PropertyContactView(data: data)
                .tabItem {
                    Image(systemName: "envelope.fill")
                    Text("Contact")
                }
        }
        .tint(.orange)
    }
}

// MARK: - Accueil View

struct PropertyAccueilView: View {
    let data: PropertyData
    let propertySlug: String
    @State private var isAnimated = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 30) {
                    // Hero Image
                    ZStack(alignment: .bottomLeading) {
                        // Use header image from Général only, otherwise show gradient
                        if let headerImage = data.general?.headerImage, !headerImage.isEmpty {
                            RemoteImage(url: APIService.headerImageURL(filename: headerImage))
                                .aspectRatio(contentMode: .fill)
                                .frame(height: 280)
                                .clipped()
                                .clipShape(RoundedRectangle(cornerRadius: 20))
                        } else {
                            LinearGradient(
                                colors: [
                                    Color(red: 0.96, green: 0.87, blue: 0.70),
                                    Color(red: 0.55, green: 0.71, blue: 0.67)
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                            .frame(height: 280)
                            .clipShape(RoundedRectangle(cornerRadius: 20))
                        }

                        LinearGradient(
                            colors: [.clear, .black.opacity(0.6)],
                            startPoint: .center,
                            endPoint: .bottom
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 20))

                        Text(data.property.name)
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundStyle(.white)
                            .shadow(color: .black.opacity(0.5), radius: 10, x: 0, y: 2)
                            .padding()
                    }
                    .padding(.horizontal)
                    .scaleEffect(isAnimated ? 1 : 0.9)
                    .opacity(isAnimated ? 1 : 0)

                    // Welcome Message
                    if let general = data.general {
                        VStack(spacing: 20) {
                            Text(general.welcomeTitle ?? "Bienvenue !")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundStyle(
                                    LinearGradient(
                                        colors: [.orange, .brown],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )

                            if let message = general.welcomeMessage {
                                Text(message)
                                    .font(.title3)
                                    .multilineTextAlignment(.center)
                                    .foregroundColor(.secondary)
                            }

                            Divider()
                                .padding(.horizontal, 50)

                            if let description = general.welcomeDescription {
                                VStack(alignment: .leading, spacing: 15) {
                                    HStack {
                                        Image(systemName: "sun.max.fill")
                                            .foregroundColor(.orange)
                                            .font(.title2)
                                        Text("Profitez de votre séjour")
                                            .font(.headline)
                                    }

                                    Text(description)
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
                        }
                        .offset(y: isAnimated ? 0 : 20)
                        .opacity(isAnimated ? 1 : 0)
                    }

                    // Quick Access - Same as Mazet BSA (WiFi, Adresse, Photos, Urgences)
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Accès rapide")
                            .font(.headline)
                            .padding(.horizontal)

                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 15) {
                            NavigationLink {
                                PropertyWiFiDetailView(data: data)
                            } label: {
                                PropertyQuickAccessCard(icon: "wifi", title: "WiFi", subtitle: "Code & infos", color: .blue)
                            }
                            .buttonStyle(PlainButtonStyle())

                            NavigationLink {
                                PropertyAdresseDetailView(data: data)
                            } label: {
                                PropertyQuickAccessCard(icon: "mappin.circle.fill", title: "Adresse", subtitle: "GPS & accès", color: .red)
                            }
                            .buttonStyle(PlainButtonStyle())

                            NavigationLink {
                                PropertyPhotosView(data: data, propertySlug: propertySlug)
                            } label: {
                                PropertyQuickAccessCard(icon: "photo.fill", title: "Photos", subtitle: "Galerie", color: .purple)
                            }
                            .buttonStyle(PlainButtonStyle())

                            NavigationLink {
                                PropertyUrgencesDetailView(data: data)
                            } label: {
                                PropertyQuickAccessCard(icon: "phone.fill", title: "Urgences", subtitle: "Numéros utiles", color: .orange)
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

// MARK: - Quick Access Card

struct PropertyQuickAccessCard: View {
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

// MARK: - Photos View

struct PropertyPhotosView: View {
    let data: PropertyData
    let propertySlug: String
    @State private var selectedPhoto: Photo?
    @State private var showingFullScreen = false

    let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10)
    ]

    var body: some View {
        ScrollView {
            if data.photos.isEmpty {
                VStack(spacing: 20) {
                    Image(systemName: "photo.on.rectangle.angled")
                        .font(.system(size: 50))
                        .foregroundColor(.secondary)
                    Text("Aucune photo disponible")
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding(.top, 100)
            } else {
                LazyVGrid(columns: columns, spacing: 10) {
                    ForEach(data.photos) { photo in
                        Button {
                            selectedPhoto = photo
                            showingFullScreen = true
                        } label: {
                            RemoteImage(propertySlug: propertySlug, filename: photo.filename)
                                .aspectRatio(1, contentMode: .fill)
                                .clipShape(RoundedRectangle(cornerRadius: 12))
                                .clipped()
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding()
            }
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("Photos")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showingFullScreen) {
            if let photo = selectedPhoto {
                PropertyFullScreenPhotoView(photo: photo, propertySlug: propertySlug)
            }
        }
    }
}

struct PropertyFullScreenPhotoView: View {
    @Environment(\.dismiss) var dismiss
    let photo: Photo
    let propertySlug: String
    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0

    var body: some View {
        NavigationStack {
            ZStack {
                Color.black.ignoresSafeArea()

                RemoteImage(propertySlug: propertySlug, filename: photo.filename)
                    .aspectRatio(contentMode: .fit)
                    .scaleEffect(scale)
                    .gesture(
                        MagnificationGesture()
                            .onChanged { value in
                                scale = lastScale * value
                            }
                            .onEnded { _ in
                                lastScale = scale
                                if scale < 1 {
                                    withAnimation { scale = 1; lastScale = 1 }
                                } else if scale > 4 {
                                    withAnimation { scale = 4; lastScale = 4 }
                                }
                            }
                    )
                    .onTapGesture(count: 2) {
                        withAnimation { scale = 1; lastScale = 1 }
                    }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Fermer") { dismiss() }
                        .foregroundColor(.white)
                }
            }
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbarBackground(Color.black.opacity(0.8), for: .navigationBar)
        }
    }
}

// MARK: - Infos Pratiques View (style Mazet BSA)

struct PropertyInfosView: View {
    let data: PropertyData
    let propertySlug: String

    var body: some View {
        NavigationStack {
            List {
                // Section WiFi
                Section {
                    NavigationLink {
                        PropertyWiFiDetailView(data: data)
                    } label: {
                        PropertyInfoRow(
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
                        PropertyAdresseDetailView(data: data)
                    } label: {
                        PropertyInfoRow(
                            icon: "mappin.circle.fill",
                            iconColor: .red,
                            title: "Adresse",
                            detail: data.address?.city ?? "Localisation"
                        )
                    }

                    if data.parking != nil {
                        NavigationLink {
                            PropertyParkingDetailView(data: data)
                        } label: {
                            PropertyInfoRow(
                                icon: "car.fill",
                                iconColor: .green,
                                title: "Parking",
                                detail: data.parking?.distance ?? "Informations"
                            )
                        }
                    }

                    if data.access != nil {
                        NavigationLink {
                            PropertyClesDetailView(data: data, propertySlug: propertySlug)
                        } label: {
                            PropertyInfoRow(
                                icon: "key.fill",
                                iconColor: .yellow,
                                title: "Clés & Accès",
                                detail: "Arrivée / Départ"
                            )
                        }
                    }
                } header: {
                    Text("Accès au logement")
                }

                // Section Urgences
                if !data.emergencies.isEmpty {
                    Section {
                        ForEach(data.emergencies) { emergency in
                            Button {
                                if let url = URL(string: "tel://\(emergency.number)") {
                                    UIApplication.shared.open(url)
                                }
                            } label: {
                                PropertyInfoRow(
                                    icon: emergencyIcon(for: emergency.name),
                                    iconColor: emergencyColor(for: emergency.name),
                                    title: emergency.name,
                                    detail: emergency.number
                                )
                            }
                            .tint(.primary)
                        }
                    } header: {
                        Text("En cas d'urgence")
                    } footer: {
                        Text("Appuyez sur un numéro pour appeler directement")
                    }
                }

                // Section Services à proximité
                if !data.services.isEmpty {
                    Section {
                        ForEach(data.services) { service in
                            NavigationLink {
                                PropertyServiceDetailView(service: service)
                            } label: {
                                PropertyInfoRow(
                                    icon: serviceIcon(for: service.category),
                                    iconColor: serviceColor(for: service.category),
                                    title: service.name,
                                    detail: service.address ?? service.category
                                )
                            }
                        }
                    } header: {
                        Text("Services à proximité")
                    }
                }
            }
            .navigationTitle("Infos Pratiques")
        }
    }

    private func emergencyIcon(for name: String) -> String {
        let lowName = name.lowercased()
        if lowName.contains("samu") { return "cross.case.fill" }
        if lowName.contains("pompier") { return "flame.fill" }
        if lowName.contains("police") { return "shield.fill" }
        return "phone.fill"
    }

    private func emergencyColor(for name: String) -> Color {
        let lowName = name.lowercased()
        if lowName.contains("samu") { return .red }
        if lowName.contains("pompier") { return .red }
        if lowName.contains("police") { return .blue }
        return .orange
    }

    private func serviceIcon(for category: String) -> String {
        let lowCat = category.lowercased()
        if lowCat.contains("pharma") { return "cross.fill" }
        if lowCat.contains("medecin") || lowCat.contains("doctor") { return "stethoscope" }
        if lowCat.contains("super") || lowCat.contains("market") { return "cart.fill" }
        if lowCat.contains("boulang") || lowCat.contains("bakery") { return "storefront.fill" }
        return "mappin.circle.fill"
    }

    private func serviceColor(for category: String) -> Color {
        let lowCat = category.lowercased()
        if lowCat.contains("pharma") { return .green }
        if lowCat.contains("medecin") || lowCat.contains("doctor") { return .blue }
        if lowCat.contains("super") || lowCat.contains("market") { return .orange }
        if lowCat.contains("boulang") || lowCat.contains("bakery") { return .brown }
        return .gray
    }
}

// MARK: - Info Row

struct PropertyInfoRow: View {
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

// MARK: - WiFi Detail View

struct PropertyWiFiDetailView: View {
    let data: PropertyData
    @State private var copied = false

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
                if let wifi = data.wifi, let ssid = wifi.ssid, let password = wifi.password {
                    VStack(spacing: 15) {
                        if let qrImage = generateWiFiQRCode(ssid: ssid, password: password) {
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

                        Text("Scannez avec l'appareil photo")
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
                                Text(ssid)
                                    .font(.body)
                                    .fontWeight(.medium)
                                    .fontDesign(.monospaced)

                                Spacer()

                                Button {
                                    UIPasteboard.general.string = ssid
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
                                Text(password)
                                    .font(.title3)
                                    .fontWeight(.semibold)
                                    .fontDesign(.monospaced)

                                Spacer()

                                Button {
                                    UIPasteboard.general.string = password
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
                }

                // Conseil
                if let wifi = data.wifi, let location = wifi.locationDescription {
                    VStack(spacing: 10) {
                        Image(systemName: "lightbulb.fill")
                            .foregroundColor(.yellow)

                        Text(location)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                }

                Spacer(minLength: 30)
            }
        }
        .background(Color(.systemGroupedBackground))
        .navigationTitle("WiFi")
        .navigationBarTitleDisplayMode(.inline)
    }

    func generateWiFiQRCode(ssid: String, password: String) -> UIImage? {
        let wifiString = "WIFI:T:WPA;S:\(ssid);P:\(password);;"

        let context = CIContext()
        let filter = CIFilter.qrCodeGenerator()

        filter.message = Data(wifiString.utf8)
        filter.correctionLevel = "H"

        guard let outputImage = filter.outputImage else { return nil }

        let transform = CGAffineTransform(scaleX: 10, y: 10)
        let scaledImage = outputImage.transformed(by: transform)

        if let cgImage = context.createCGImage(scaledImage, from: scaledImage.extent) {
            return UIImage(cgImage: cgImage)
        }

        return nil
    }
}

// MARK: - Adresse Detail View

struct PropertyAdresseDetailView: View {
    let data: PropertyData

    var body: some View {
        List {
            if let address = data.address {
                // Section carte
                Section {
                    MapSnapshotView(address: address.fullAddress)
                        .frame(height: 250)
                        .cornerRadius(12)
                        .listRowInsets(EdgeInsets())
                }

                Section {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(data.property.name)
                            .font(.headline)
                        if let street = address.street {
                            Text(street)
                                .font(.body)
                        }
                        if let postalCode = address.postalCode, let city = address.city {
                            Text("\(postalCode) \(city)")
                                .font(.body)
                        }
                        if let country = address.country {
                            Text(country)
                                .font(.body)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 5)

                    Button {
                        let fullAddress = address.fullAddress
                        if let encoded = fullAddress.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                           let url = URL(string: "maps://?address=\(encoded)") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        Label("Ouvrir dans Plans", systemImage: "map.fill")
                    }
                } header: {
                    Text("Adresse")
                }

                if let description = address.description {
                    Section {
                        Text(description)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    } header: {
                        Text("Localisation")
                    }
                }
            }
        }
        .navigationTitle("Adresse")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Parking Detail View

struct PropertyParkingDetailView: View {
    let data: PropertyData

    var body: some View {
        List {
            if let parking = data.parking {
                Section {
                    VStack(alignment: .leading, spacing: 15) {
                        HStack {
                            Image(systemName: parking.isFree == true ? "checkmark.circle.fill" : "eurosign.circle.fill")
                                .foregroundColor(parking.isFree == true ? .green : .orange)
                            Text(parking.isFree == true ? "Parking gratuit" : "Parking payant")
                                .fontWeight(.medium)
                        }

                        if let desc = parking.description {
                            Text(desc)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 5)
                } header: {
                    Text("Stationnement")
                }

                if let tips = parking.tips {
                    Section {
                        Text("💡 Conseil : \(tips)")
                            .font(.subheadline)
                    }
                }
            }
        }
        .navigationTitle("Parking")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Clés Detail View

struct PropertyClesDetailView: View {
    let data: PropertyData
    let propertySlug: String

    var body: some View {
        List {
            if let access = data.access {
                Section {
                    VStack(alignment: .leading, spacing: 10) {
                        if let checkIn = access.checkInTime {
                            Label("Arrivée : \(checkIn)", systemImage: "arrow.right.circle.fill")
                                .font(.headline)
                                .foregroundColor(.green)
                        }

                        if let checkOut = access.checkOutTime {
                            Label("Départ : \(checkOut)", systemImage: "arrow.left.circle.fill")
                                .font(.headline)
                                .foregroundColor(.orange)
                        }
                    }
                    .padding(.vertical, 5)
                } header: {
                    Text("Horaires")
                }

                if let keyboxCode = access.keyboxCode {
                    Section {
                        VStack(spacing: 15) {
                            // Code de la boîte à clés
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Code de la boîte à clés")
                                    .font(.headline)
                                    .foregroundColor(.primary)

                                HStack {
                                    Image(systemName: "lock.square.fill")
                                        .font(.title2)
                                        .foregroundColor(.orange)

                                    Text(keyboxCode)
                                        .font(.system(size: 32, weight: .bold, design: .monospaced))
                                        .foregroundColor(.primary)

                                    Spacer()

                                    Button {
                                        UIPasteboard.general.string = keyboxCode
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

                            if let location = access.keyboxLocation {
                                Text(location)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 5)
                    } header: {
                        Text("Récupération des clés")
                    }
                }

                if let instructions = access.accessInstructions {
                    Section {
                        Text(instructions)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    } header: {
                        Text("Instructions d'accès")
                    }
                }

                // Access Photos
                if !data.accessPhotos.isEmpty {
                    Section {
                        ForEach(data.accessPhotos) { photo in
                            VStack(spacing: 10) {
                                RemoteImage(propertySlug: propertySlug, filename: photo.filename, isAccessPhoto: true)
                                    .aspectRatio(contentMode: .fill)
                                    .frame(height: 200)
                                    .clipped()
                                    .cornerRadius(12)

                                if let title = photo.title {
                                    Text(title)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                    } header: {
                        Text("Photos d'accès")
                    }
                }
            }
        }
        .navigationTitle("Clés & Accès")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Urgences Detail View

struct PropertyUrgencesDetailView: View {
    let data: PropertyData

    var body: some View {
        List {
            Section {
                ForEach(data.emergencies) { emergency in
                    Button {
                        if let url = URL(string: "tel://\(emergency.number)") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        PropertyInfoRow(
                            icon: emergencyIcon(for: emergency.name),
                            iconColor: emergencyColor(for: emergency.name),
                            title: emergency.name,
                            detail: emergency.number
                        )
                    }
                    .tint(.primary)
                }
            } header: {
                Text("En cas d'urgence")
            } footer: {
                Text("Appuyez sur un numéro pour appeler directement")
            }
        }
        .navigationTitle("Urgences")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func emergencyIcon(for name: String) -> String {
        let lowName = name.lowercased()
        if lowName.contains("samu") { return "cross.case.fill" }
        if lowName.contains("pompier") { return "flame.fill" }
        if lowName.contains("police") { return "shield.fill" }
        return "phone.fill"
    }

    private func emergencyColor(for name: String) -> Color {
        let lowName = name.lowercased()
        if lowName.contains("samu") { return .red }
        if lowName.contains("pompier") { return .red }
        if lowName.contains("police") { return .blue }
        return .orange
    }
}

// MARK: - Service Detail View

struct PropertyServiceDetailView: View {
    let service: NearbyService

    var body: some View {
        List {
            if let address = service.address {
                Section {
                    MapSnapshotView(address: "\(service.name), \(address)")
                        .frame(height: 250)
                        .cornerRadius(12)
                        .listRowInsets(EdgeInsets())
                }
            }

            Section {
                VStack(alignment: .leading, spacing: 10) {
                    Text(service.name)
                        .font(.headline)
                    if let address = service.address {
                        Text(address)
                            .font(.body)
                    }
                }
                .padding(.vertical, 5)

                if let address = service.address {
                    Button {
                        if let encoded = address.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
                           let url = URL(string: "maps://?address=\(encoded)") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        Label("Ouvrir dans Plans", systemImage: "map.fill")
                    }
                }

                if let phone = service.phone {
                    Button {
                        if let url = URL(string: "tel://\(phone)") {
                            UIApplication.shared.open(url)
                        }
                    } label: {
                        Label("Appeler", systemImage: "phone.fill")
                    }
                }
            } header: {
                Text("Adresse & Contact")
            }

            if let hours = service.openingHours {
                Section {
                    Text(hours)
                        .font(.subheadline)
                } header: {
                    Text("Horaires")
                }
            }

            if let description = service.description {
                Section {
                    Text(description)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                } header: {
                    Text("Informations")
                }
            }
        }
        .navigationTitle(service.name)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Activities View

struct PropertyActivitesView: View {
    let data: PropertyData

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    ForEach(data.activityCategories) { category in
                        let categoryActivities = data.activities.filter { $0.category == category.name }

                        if !categoryActivities.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                HStack {
                                    Text(category.icon ?? "⭐")
                                    Text(category.name)
                                        .font(.headline)
                                }

                                ForEach(categoryActivities) { activity in
                                    HStack(alignment: .top, spacing: 12) {
                                        Text(activity.emoji ?? "📍")
                                            .font(.title2)

                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(activity.name)
                                                .font(.subheadline)
                                                .fontWeight(.medium)

                                            if let desc = activity.description {
                                                Text(desc)
                                                    .font(.caption)
                                                    .foregroundColor(.secondary)
                                            }

                                            if let distance = activity.distance {
                                                Text(distance)
                                                    .font(.caption2)
                                                    .foregroundColor(.blue)
                                            }
                                        }
                                    }
                                }
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color(.systemBackground))
                                    .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
                            )
                        }
                    }

                    if data.activityCategories.isEmpty && data.activities.isEmpty {
                        VStack(spacing: 20) {
                            Image(systemName: "star.slash")
                                .font(.system(size: 50))
                                .foregroundColor(.secondary)
                            Text("Aucune activité disponible")
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.top, 100)
                    }
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Activités")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// MARK: - Contact View

struct PropertyContactView: View {
    let data: PropertyData

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    if let contact = data.contact {
                        VStack(spacing: 20) {
                            // Host info
                            if let name = contact.hostName {
                                VStack(spacing: 10) {
                                    // Avatar or placeholder
                                    if let avatarFilename = contact.avatar, !avatarFilename.isEmpty {
                                        RemoteImage(url: APIService.avatarURL(filename: avatarFilename)) {
                                            ZStack {
                                                Circle()
                                                    .fill(
                                                        LinearGradient(
                                                            colors: [.orange, .brown],
                                                            startPoint: .topLeading,
                                                            endPoint: .bottomTrailing
                                                        )
                                                    )
                                                Text(name.prefix(1).uppercased())
                                                    .font(.largeTitle)
                                                    .fontWeight(.bold)
                                                    .foregroundColor(.white)
                                            }
                                        }
                                        .aspectRatio(contentMode: .fill)
                                        .frame(width: 80, height: 80)
                                        .clipShape(Circle())
                                    } else {
                                        ZStack {
                                            Circle()
                                                .fill(
                                                    LinearGradient(
                                                        colors: [.orange, .brown],
                                                        startPoint: .topLeading,
                                                        endPoint: .bottomTrailing
                                                    )
                                                )
                                                .frame(width: 80, height: 80)

                                            Text(name.prefix(1).uppercased())
                                                .font(.largeTitle)
                                                .fontWeight(.bold)
                                                .foregroundColor(.white)
                                        }
                                    }

                                    Text(name)
                                        .font(.title2)
                                        .fontWeight(.semibold)

                                    if let description = contact.description {
                                        Text(description)
                                            .font(.subheadline)
                                            .foregroundColor(.secondary)
                                            .multilineTextAlignment(.center)
                                    }

                                    if let responseTime = contact.responseTime {
                                        HStack {
                                            Image(systemName: "clock")
                                                .foregroundColor(.orange)
                                            Text(responseTime)
                                                .font(.caption)
                                                .foregroundColor(.secondary)
                                        }
                                    }
                                }
                                .padding()
                            }

                            // Contact buttons
                            VStack(spacing: 12) {
                                if let phone = contact.phone, !phone.isEmpty {
                                    PropertyContactButton(
                                        icon: "phone.fill",
                                        title: "Appeler",
                                        subtitle: phone,
                                        color: .green,
                                        action: { callPhone(phone) }
                                    )
                                }

                                if let whatsapp = contact.whatsapp, !whatsapp.isEmpty {
                                    PropertyContactButton(
                                        icon: "message.fill",
                                        title: "WhatsApp",
                                        subtitle: whatsapp,
                                        color: .green,
                                        action: { openWhatsApp(whatsapp) }
                                    )
                                }

                                if let email = contact.email, !email.isEmpty {
                                    PropertyContactButton(
                                        icon: "envelope.fill",
                                        title: "Email",
                                        subtitle: email,
                                        color: .blue,
                                        action: { sendEmail(email) }
                                    )
                                }

                                if let airbnbUrl = contact.airbnbUrl, !airbnbUrl.isEmpty {
                                    PropertyContactButton(
                                        icon: "house.fill",
                                        title: "Airbnb",
                                        subtitle: "Voir l'annonce",
                                        color: .pink,
                                        action: { openURL(airbnbUrl) }
                                    )
                                }
                            }
                            .padding(.horizontal)
                        }
                    } else {
                        VStack(spacing: 20) {
                            Image(systemName: "person.crop.circle.badge.questionmark")
                                .font(.system(size: 50))
                                .foregroundColor(.secondary)
                            Text("Aucune information de contact")
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.top, 100)
                    }
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Contact")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    private func callPhone(_ number: String) {
        if let url = URL(string: "tel://\(number.replacingOccurrences(of: " ", with: ""))") {
            UIApplication.shared.open(url)
        }
    }

    private func openWhatsApp(_ number: String) {
        let cleanNumber = number.replacingOccurrences(of: " ", with: "").replacingOccurrences(of: "+", with: "")
        if let url = URL(string: "https://wa.me/\(cleanNumber)") {
            UIApplication.shared.open(url)
        }
    }

    private func sendEmail(_ email: String) {
        if let url = URL(string: "mailto:\(email)") {
            UIApplication.shared.open(url)
        }
    }

    private func openURL(_ urlString: String) {
        if let url = URL(string: urlString) {
            UIApplication.shared.open(url)
        }
    }
}

struct PropertyContactButton: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                    .frame(width: 40)

                VStack(alignment: .leading) {
                    Text(title)
                        .font(.headline)
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemBackground))
                    .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
            )
        }
        .foregroundColor(.primary)
    }
}

#Preview {
    PropertyDetailView(reservation: Reservation(
        id: 1,
        propertyId: 1,
        propertyName: "Le Mazet",
        propertySlug: "mazet-bsa",
        propertyIcon: "🏠",
        city: "Bourg-Saint-Andéol",
        street: nil,
        bookingUrl: nil,
        personalComment: nil,
        addedAt: "",
        expiresAt: ""
    ))
}
