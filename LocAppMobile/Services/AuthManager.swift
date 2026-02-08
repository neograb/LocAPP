import Foundation
import SwiftUI
import Combine

@MainActor
class AuthManager: ObservableObject {
    @Published var currentUser: User?
    @Published var isAuthenticated: Bool = false
    @Published var isLoading: Bool = false
    @Published var error: String?

    private let api = APIService.shared

    init() {
        // Check if already logged in
        if api.isLoggedIn() {
            Task {
                await checkAuth()
            }
        }
    }

    func checkAuth() async {
        do {
            let response = try await api.getCurrentUser()
            currentUser = response.user
            isAuthenticated = true
        } catch {
            isAuthenticated = false
            currentUser = nil
            api.clearAuth()
        }
    }

    func login(email: String, password: String) async -> Bool {
        isLoading = true
        error = nil

        do {
            let response = try await api.login(email: email, password: password)
            currentUser = response.user
            isAuthenticated = true
            isLoading = false
            return true
        } catch let apiError as APIError {
            error = apiError.errorDescription
            isLoading = false
            return false
        } catch {
            self.error = "Erreur de connexion"
            isLoading = false
            return false
        }
    }

    func register(email: String, firstname: String, lastname: String, password: String) async -> Bool {
        isLoading = true
        error = nil

        do {
            let response = try await api.register(email: email, firstname: firstname, lastname: lastname, password: password)
            currentUser = response.user
            isAuthenticated = true
            isLoading = false
            return true
        } catch let apiError as APIError {
            error = apiError.errorDescription
            isLoading = false
            return false
        } catch {
            self.error = "Erreur lors de l'inscription"
            isLoading = false
            return false
        }
    }

    func logout() async {
        do {
            try await api.logout()
        } catch {
            // Logout locally even if server fails
        }
        currentUser = nil
        isAuthenticated = false
    }

    func updateProfile(firstname: String?, lastname: String?, password: String?) async -> Bool {
        isLoading = true
        error = nil

        do {
            let response = try await api.updateProfile(firstname: firstname, lastname: lastname, password: password)
            currentUser = response.user
            isLoading = false
            return true
        } catch let apiError as APIError {
            error = apiError.errorDescription
            isLoading = false
            return false
        } catch {
            self.error = "Erreur lors de la mise à jour"
            isLoading = false
            return false
        }
    }

    func deleteAccount() async -> Bool {
        isLoading = true
        error = nil

        do {
            try await api.deleteAccount()
            currentUser = nil
            isAuthenticated = false
            isLoading = false
            return true
        } catch let apiError as APIError {
            error = apiError.errorDescription
            isLoading = false
            return false
        } catch {
            self.error = "Erreur lors de la suppression"
            isLoading = false
            return false
        }
    }
}
