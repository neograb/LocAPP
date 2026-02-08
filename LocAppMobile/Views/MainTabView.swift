import SwiftUI
import Combine

struct MainTabView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var reservationManager = ReservationManager()

    var body: some View {
        TabView {
            // Mes Réservations
            ReservationsView()
                .environmentObject(reservationManager)
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("Réservations")
                }

            // Historique
            HistoryView()
                .tabItem {
                    Image(systemName: "clock.fill")
                    Text("Historique")
                }

            // Mon Compte
            AccountView()
                .tabItem {
                    Image(systemName: "person.fill")
                    Text("Compte")
                }
        }
        .tint(.orange)
        .onAppear {
            Task {
                await reservationManager.loadReservations()
            }
        }
    }
}

// MARK: - Reservation Manager

@MainActor
class ReservationManager: ObservableObject {
    @Published var reservations: [Reservation] = []
    @Published var isLoading = false
    @Published var error: String?

    private let api = APIService.shared

    func loadReservations() async {
        isLoading = true
        error = nil

        do {
            let response = try await api.getReservations()
            reservations = response.reservations
        } catch let apiError as APIError {
            error = apiError.errorDescription
        } catch {
            self.error = "Erreur de chargement"
        }

        isLoading = false
    }

    func removeReservation(_ reservation: Reservation) async {
        do {
            try await api.removeReservation(reservation.id)
            reservations.removeAll { $0.id == reservation.id }

            // Delete cached photos for this property
            PhotoCacheManager.shared.deletePhotosForProperty(propertySlug: reservation.propertySlug)
        } catch {
            self.error = "Erreur lors de la suppression"
        }
    }
}

#Preview {
    MainTabView()
        .environmentObject(AuthManager())
}
