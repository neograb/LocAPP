import SwiftUI

struct AccountView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var showEditProfile = false
    @State private var showDeleteConfirmation = false

    var body: some View {
        NavigationStack {
            List {
                // User Info Section
                Section {
                    if let user = authManager.currentUser {
                        HStack(spacing: 15) {
                            // Avatar
                            ZStack {
                                Circle()
                                    .fill(
                                        LinearGradient(
                                            colors: [.orange, .brown],
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing
                                        )
                                    )
                                    .frame(width: 60, height: 60)

                                Text(user.firstname.prefix(1).uppercased())
                                    .font(.title2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                            }

                            VStack(alignment: .leading, spacing: 4) {
                                Text(user.fullName)
                                    .font(.headline)

                                Text(user.email)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                }

                // Profile Actions
                Section("Paramètres") {
                    Button(action: { showEditProfile = true }) {
                        HStack {
                            Image(systemName: "person.fill")
                                .foregroundColor(.blue)
                            Text("Modifier mon profil")
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .foregroundColor(.primary)
                }

                // Logout
                Section {
                    Button(action: logout) {
                        HStack {
                            Image(systemName: "rectangle.portrait.and.arrow.right")
                                .foregroundColor(.orange)
                            Text("Se déconnecter")
                        }
                    }
                    .foregroundColor(.primary)
                }

                // Delete Account
                Section {
                    Button(action: { showDeleteConfirmation = true }) {
                        HStack {
                            Image(systemName: "trash.fill")
                                .foregroundColor(.red)
                            Text("Supprimer mon compte")
                        }
                    }
                    .foregroundColor(.red)
                }
            }
            .navigationTitle("Mon Compte")
            .sheet(isPresented: $showEditProfile) {
                EditProfileView()
                    .environmentObject(authManager)
            }
            .confirmationDialog(
                "Supprimer mon compte",
                isPresented: $showDeleteConfirmation,
                titleVisibility: .visible
            ) {
                Button("Supprimer définitivement", role: .destructive) {
                    deleteAccount()
                }
                Button("Annuler", role: .cancel) {}
            } message: {
                Text("Cette action est irréversible. Toutes vos données seront supprimées.")
            }
        }
    }

    private func logout() {
        Task {
            await authManager.logout()
        }
    }

    private func deleteAccount() {
        Task {
            await authManager.deleteAccount()
        }
    }
}

// MARK: - Edit Profile View

struct EditProfileView: View {
    @EnvironmentObject var authManager: AuthManager
    @Environment(\.dismiss) var dismiss

    @State private var firstname = ""
    @State private var lastname = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var localError: String?

    var body: some View {
        NavigationStack {
            Form {
                Section("Informations personnelles") {
                    TextField("Prénom", text: $firstname)
                    TextField("Nom", text: $lastname)
                }

                Section("Changer le mot de passe") {
                    SecureField("Nouveau mot de passe", text: $newPassword)
                    SecureField("Confirmer", text: $confirmPassword)
                }

                if let error = localError ?? authManager.error {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
            }
            .navigationTitle("Modifier mon profil")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Annuler") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Enregistrer") {
                        saveProfile()
                    }
                    .disabled(authManager.isLoading)
                }
            }
            .onAppear {
                if let user = authManager.currentUser {
                    firstname = user.firstname
                    lastname = user.lastname
                }
            }
        }
    }

    private func saveProfile() {
        localError = nil

        var password: String? = nil
        if !newPassword.isEmpty {
            guard newPassword == confirmPassword else {
                localError = "Les mots de passe ne correspondent pas"
                return
            }
            guard newPassword.count >= 6 else {
                localError = "Le mot de passe doit contenir au moins 6 caractères"
                return
            }
            password = newPassword
        }

        Task {
            let success = await authManager.updateProfile(
                firstname: firstname.isEmpty ? nil : firstname,
                lastname: lastname.isEmpty ? nil : lastname,
                password: password
            )
            if success {
                dismiss()
            }
        }
    }
}

#Preview {
    AccountView()
        .environmentObject(AuthManager())
}
