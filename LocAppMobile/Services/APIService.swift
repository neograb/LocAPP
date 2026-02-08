import Foundation
import Combine

// MARK: - API Service

class APIService {
    static let shared = APIService()

    // Configure this with your server URL
    // Use your Mac's local IP when testing on a real device
    #if DEBUG
    private let baseURL = "http://192.168.68.65:5001/api/mobile"
    static let serverURL = "http://192.168.68.65:5001"
    #else
    private let baseURL = "https://your-production-url.com/api/mobile"
    static let serverURL = "https://your-production-url.com"
    #endif

    /// Get the full URL for a property photo
    static func photoURL(propertySlug: String, filename: String) -> URL? {
        return URL(string: "\(serverURL)/uploads/properties/\(propertySlug)/photos/\(filename)")
    }

    /// Get the full URL for an access photo
    static func accessPhotoURL(propertySlug: String, filename: String) -> URL? {
        return URL(string: "\(serverURL)/uploads/properties/\(propertySlug)/access/\(filename)")
    }

    /// Get the full URL for a contact avatar
    static func avatarURL(filename: String) -> URL? {
        return URL(string: "\(serverURL)/uploads/avatars/\(filename)")
    }

    /// Get the full URL for a header image
    static func headerImageURL(filename: String) -> URL? {
        return URL(string: "\(serverURL)/uploads/headers/\(filename)")
    }

    private var authToken: String? {
        get { UserDefaults.standard.string(forKey: "authToken") }
        set { UserDefaults.standard.set(newValue, forKey: "authToken") }
    }

    private init() {}

    // MARK: - Generic Request Method

    private func request<T: Decodable>(_ endpoint: String, method: String = "GET", body: [String: Any]? = nil) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        if httpResponse.statusCode >= 400 {
            if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
                throw APIError.serverError(errorResponse.error)
            }
            throw APIError.serverError("Erreur \(httpResponse.statusCode)")
        }

        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch let decodingError as DecodingError {
            print("❌ Decoding Error: \(decodingError)")
            if let jsonString = String(data: data, encoding: .utf8) {
                print("📦 Raw JSON (first 500 chars): \(String(jsonString.prefix(500)))")
            }
            throw APIError.serverError("Erreur de décodage: \(decodingError.localizedDescription)")
        }
    }

    // MARK: - Authentication

    func register(email: String, firstname: String, lastname: String, password: String) async throws -> AuthResponse {
        let response: AuthResponse = try await request("/auth/register", method: "POST", body: [
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "password": password
        ])
        authToken = response.token
        return response
    }

    func login(email: String, password: String) async throws -> AuthResponse {
        let response: AuthResponse = try await request("/auth/login", method: "POST", body: [
            "email": email,
            "password": password
        ])
        authToken = response.token
        return response
    }

    func logout() async throws {
        let _: SuccessResponse = try await request("/auth/logout", method: "POST")
        authToken = nil
    }

    func getCurrentUser() async throws -> UserResponse {
        return try await request("/auth/me")
    }

    func updateProfile(firstname: String?, lastname: String?, password: String?) async throws -> UserResponse {
        var body: [String: Any] = [:]
        if let firstname = firstname { body["firstname"] = firstname }
        if let lastname = lastname { body["lastname"] = lastname }
        if let password = password { body["password"] = password }
        return try await request("/auth/update", method: "PUT", body: body)
    }

    func deleteAccount() async throws {
        let _: SuccessResponse = try await request("/auth/delete", method: "DELETE")
        authToken = nil
    }

    // MARK: - Token Validation

    func validateToken(_ code: String, bookingURL: String? = nil) async throws -> TokenValidationResponse {
        var body: [String: Any] = ["token": code]
        if let url = bookingURL { body["booking_url"] = url }
        return try await request("/token/validate", method: "POST", body: body)
    }

    // MARK: - Reservations

    func getReservations() async throws -> ReservationsResponse {
        return try await request("/reservations")
    }

    func removeReservation(_ id: Int) async throws {
        let _: SuccessResponse = try await request("/reservations/\(id)", method: "DELETE")
    }

    func updateReservationComment(_ id: Int, comment: String) async throws {
        let _: SuccessResponse = try await request("/reservations/\(id)/comment", method: "PUT", body: ["comment": comment])
    }

    func getPropertyData(reservationId: Int) async throws -> PropertyData {
        return try await request("/reservations/\(reservationId)/property")
    }

    // MARK: - History

    func getHistory() async throws -> HistoryResponse {
        return try await request("/history")
    }

    func deleteHistoryEntry(_ id: Int) async throws {
        let _: SuccessResponse = try await request("/history/\(id)", method: "DELETE")
    }

    // MARK: - Helper

    func isLoggedIn() -> Bool {
        return authToken != nil
    }

    func clearAuth() {
        authToken = nil
    }
}

// MARK: - API Errors

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case serverError(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "URL invalide"
        case .invalidResponse: return "Réponse invalide"
        case .unauthorized: return "Non authentifié"
        case .serverError(let message): return message
        }
    }
}

// MARK: - Response Models

struct ErrorResponse: Decodable {
    let error: String
}

struct SuccessResponse: Decodable {
    let success: Bool
}

struct AuthResponse: Decodable {
    let success: Bool
    let token: String
    let user: User
}

struct UserResponse: Decodable {
    let user: User
}

struct User: Decodable, Identifiable {
    let id: Int
    let email: String
    let firstname: String
    let lastname: String
    var createdAt: String?

    var fullName: String {
        "\(firstname) \(lastname)"
    }

    enum CodingKeys: String, CodingKey {
        case id, email, firstname, lastname
        case createdAt = "created_at"
    }
}

struct TokenValidationResponse: Decodable {
    let success: Bool
    let reservationId: Int
    let propertyName: String
    let propertySlug: String
    let validUntil: String

    enum CodingKeys: String, CodingKey {
        case success
        case reservationId = "reservation_id"
        case propertyName = "property_name"
        case propertySlug = "property_slug"
        case validUntil = "valid_until"
    }
}

struct ReservationsResponse: Decodable {
    let reservations: [Reservation]
}

struct Reservation: Decodable, Identifiable, Hashable {
    let id: Int
    let propertyId: Int
    let propertyName: String
    let propertySlug: String
    let propertyIcon: String?
    let city: String?
    let street: String?
    let bookingUrl: String?
    let personalComment: String?
    let addedAt: String
    let expiresAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case propertyId = "property_id"
        case propertyName = "property_name"
        case propertySlug = "property_slug"
        case propertyIcon = "property_icon"
        case city, street
        case bookingUrl = "booking_url"
        case personalComment = "personal_comment"
        case addedAt = "added_at"
        case expiresAt = "expires_at"
    }
}

struct HistoryResponse: Decodable {
    let history: [HistoryEntry]
}

struct HistoryEntry: Decodable, Identifiable {
    let id: Int
    let propertyName: String
    let propertySlug: String?
    let propertyAddress: String?
    let bookingUrl: String?
    let personalComment: String?
    let stayedFrom: String?
    let stayedUntil: String?
    let archivedAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case propertyName = "property_name"
        case propertySlug = "property_slug"
        case propertyAddress = "property_address"
        case bookingUrl = "booking_url"
        case personalComment = "personal_comment"
        case stayedFrom = "stayed_from"
        case stayedUntil = "stayed_until"
        case archivedAt = "archived_at"
    }
}
