import SwiftUI

struct ReservationsView: View {
    @EnvironmentObject var reservationManager: ReservationManager
    @State private var showTokenInput = false
    @State private var selectedReservation: Reservation?

    var body: some View {
        NavigationStack {
            ZStack {
                if reservationManager.isLoading && reservationManager.reservations.isEmpty {
                    ProgressView("Chargement...")
                } else if reservationManager.reservations.isEmpty {
                    // Empty state - show token input
                    EmptyReservationsView(showTokenInput: $showTokenInput)
                } else {
                    // List of reservations
                    List {
                        ForEach(reservationManager.reservations) { reservation in
                            NavigationLink(destination: PropertyDetailView(reservation: reservation)) {
                                ReservationRow(reservation: reservation)
                            }
                        }
                        .onDelete(perform: deleteReservation)

                        // Add more button
                        Section {
                            Button(action: { showTokenInput = true }) {
                                HStack {
                                    Image(systemName: "plus.circle.fill")
                                        .foregroundColor(.orange)
                                    Text("Ajouter une réservation")
                                        .foregroundColor(.orange)
                                }
                            }
                        }
                    }
                    .refreshable {
                        await reservationManager.loadReservations()
                    }
                }
            }
            .navigationTitle("Mes Réservations")
            .toolbar {
                if !reservationManager.reservations.isEmpty {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button(action: { showTokenInput = true }) {
                            Image(systemName: "plus")
                        }
                    }
                }
            }
            .sheet(isPresented: $showTokenInput) {
                TokenInputView {
                    await reservationManager.loadReservations()
                }
            }
        }
    }

    private func deleteReservation(at offsets: IndexSet) {
        for index in offsets {
            let reservation = reservationManager.reservations[index]
            Task {
                await reservationManager.removeReservation(reservation)
            }
        }
    }
}

// MARK: - Empty State

struct EmptyReservationsView: View {
    @Binding var showTokenInput: Bool

    var body: some View {
        VStack(spacing: 25) {
            Image(systemName: "key.fill")
                .font(.system(size: 60))
                .foregroundColor(.orange.opacity(0.7))

            VStack(spacing: 10) {
                Text("Aucune réservation")
                    .font(.title2)
                    .fontWeight(.semibold)

                Text("Saisissez le code fourni par votre hôte pour accéder aux informations de votre location")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 30)
            }

            Button(action: { showTokenInput = true }) {
                HStack {
                    Image(systemName: "keyboard")
                    Text("Saisir un code")
                }
                .fontWeight(.semibold)
                .frame(maxWidth: .infinity)
                .padding()
                .background(
                    LinearGradient(
                        colors: [.orange, .brown],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            .padding(.horizontal, 40)
        }
        .padding()
    }
}

// MARK: - Reservation Row

struct ReservationRow: View {
    let reservation: Reservation

    var body: some View {
        HStack(spacing: 15) {
            // Icon
            Text(reservation.propertyIcon ?? "🏠")
                .font(.title)
                .frame(width: 50, height: 50)
                .background(Color.orange.opacity(0.1))
                .cornerRadius(10)

            VStack(alignment: .leading, spacing: 4) {
                Text(reservation.propertyName)
                    .font(.headline)

                if let city = reservation.city {
                    Text(city)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }

                // Expiration
                HStack(spacing: 4) {
                    Image(systemName: "clock")
                        .font(.caption)
                    Text("Expire: \(formatDate(reservation.expiresAt))")
                        .font(.caption)
                }
                .foregroundColor(.orange)
            }

            Spacer()
        }
        .padding(.vertical, 5)
    }

    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate, .withTime, .withColonSeparatorInTime]

        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateFormat = "dd/MM/yyyy"
            displayFormatter.locale = Locale(identifier: "fr_FR")
            return displayFormatter.string(from: date)
        }
        return dateString
    }
}

#Preview {
    ReservationsView()
        .environmentObject(ReservationManager())
}
