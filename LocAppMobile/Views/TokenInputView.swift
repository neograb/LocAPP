import SwiftUI

struct TokenInputView: View {
    @Environment(\.dismiss) var dismiss
    @State private var tokenCode = ""
    @State private var bookingUrl = ""
    @State private var isLoading = false
    @State private var error: String?
    @State private var success: TokenValidationResponse?

    var onSuccess: () async -> Void

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 25) {
                    // Header
                    VStack(spacing: 15) {
                        Image(systemName: "key.fill")
                            .font(.system(size: 50))
                            .foregroundColor(.orange)

                        Text("Ajouter une réservation")
                            .font(.title2)
                            .fontWeight(.bold)

                        Text("Saisissez le code d'accès fourni par votre hôte")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, 30)

                    if let success = success {
                        // Success state
                        SuccessView(response: success) {
                            Task {
                                await onSuccess()
                                dismiss()
                            }
                        }
                    } else {
                        // Input form
                        VStack(spacing: 20) {
                            // Token input
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Code d'accès")
                                    .font(.subheadline)
                                    .fontWeight(.medium)

                                TextField("ABC123", text: $tokenCode)
                                    .textFieldStyle(RoundedTextFieldStyle())
                                    .font(.title2.monospaced())
                                    .multilineTextAlignment(.center)
                                    .autocapitalization(.allCharacters)
                                    .onChange(of: tokenCode) { _, newValue in
                                        tokenCode = newValue.uppercased()
                                    }
                            }

                            // Optional booking URL
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Text("Lien de réservation")
                                        .font(.subheadline)
                                        .fontWeight(.medium)
                                    Text("(optionnel)")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }

                                TextField("https://airbnb.com/...", text: $bookingUrl)
                                    .textFieldStyle(RoundedTextFieldStyle())
                                    .keyboardType(.URL)
                                    .autocapitalization(.none)
                            }

                            if let error = error {
                                Text(error)
                                    .font(.caption)
                                    .foregroundColor(.red)
                                    .padding()
                                    .background(Color.red.opacity(0.1))
                                    .cornerRadius(8)
                            }

                            Button(action: validateToken) {
                                HStack {
                                    if isLoading {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    } else {
                                        Image(systemName: "checkmark.circle.fill")
                                        Text("Valider")
                                    }
                                }
                                .fontWeight(.semibold)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(
                                    LinearGradient(
                                        colors: tokenCode.count >= 6 ? [.orange, .brown] : [.gray, .gray],
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    )
                                )
                                .foregroundColor(.white)
                                .cornerRadius(12)
                            }
                            .disabled(isLoading || tokenCode.count < 6)
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 20)
                                .fill(Color(.systemBackground))
                                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
                        )
                        .padding(.horizontal)
                    }

                    Spacer()
                }
            }
            .background(Color(.systemGroupedBackground))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Annuler") {
                        dismiss()
                    }
                }
            }
        }
    }

    private func validateToken() {
        isLoading = true
        error = nil

        Task {
            do {
                let response = try await APIService.shared.validateToken(
                    tokenCode,
                    bookingURL: bookingUrl.isEmpty ? nil : bookingUrl
                )
                success = response
            } catch let apiError as APIError {
                error = apiError.errorDescription
            } catch {
                self.error = "Erreur de validation"
            }
            isLoading = false
        }
    }
}

// MARK: - Success View

struct SuccessView: View {
    let response: TokenValidationResponse
    var onContinue: () -> Void

    @StateObject private var cacheManager = PhotoCacheManager.shared

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text("Code validé !")
                .font(.title2)
                .fontWeight(.bold)

            VStack(spacing: 8) {
                Text(response.propertyName)
                    .font(.headline)

                Text("Valide jusqu'au \(formatDate(response.validUntil))")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.green.opacity(0.1))
            .cornerRadius(12)

            // Download progress
            if cacheManager.isDownloading {
                VStack(spacing: 8) {
                    ProgressView(value: cacheManager.downloadProgress)
                        .progressViewStyle(LinearProgressViewStyle(tint: .orange))

                    Text("Téléchargement des photos... \(Int(cacheManager.downloadProgress * 100))%")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
            }

            Button(action: onContinue) {
                Text("Accéder à la propriété")
                    .fontWeight(.semibold)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        LinearGradient(
                            colors: cacheManager.isDownloading ? [.gray, .gray] : [.green, .teal],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
            .disabled(cacheManager.isDownloading)
            .padding(.horizontal)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
        )
        .padding(.horizontal)
        .task {
            // Download photos in background
            await cacheManager.downloadPhotosForProperty(
                reservationId: response.reservationId,
                propertySlug: response.propertySlug
            )
        }
    }

    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate, .withTime, .withColonSeparatorInTime]

        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateFormat = "dd MMMM yyyy"
            displayFormatter.locale = Locale(identifier: "fr_FR")
            return displayFormatter.string(from: date)
        }
        return dateString
    }
}

#Preview {
    TokenInputView { }
}
