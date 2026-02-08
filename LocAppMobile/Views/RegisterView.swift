import SwiftUI

struct RegisterView: View {
    @EnvironmentObject var authManager: AuthManager
    @Environment(\.dismiss) var dismiss

    @State private var email = ""
    @State private var firstname = ""
    @State private var lastname = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var localError: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 25) {
                    // Header
                    VStack(spacing: 10) {
                        Image(systemName: "person.badge.plus")
                            .font(.system(size: 50))
                            .foregroundColor(.orange)

                        Text("Créer un compte")
                            .font(.title)
                            .fontWeight(.bold)

                        Text("Rejoignez LocApp pour accéder à vos locations")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding(.top, 20)

                    // Form
                    VStack(spacing: 18) {
                        HStack(spacing: 12) {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("Prénom")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                TextField("Jean", text: $firstname)
                                    .textFieldStyle(RoundedTextFieldStyle())
                                    .textContentType(.givenName)
                            }

                            VStack(alignment: .leading, spacing: 6) {
                                Text("Nom")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                TextField("Dupont", text: $lastname)
                                    .textFieldStyle(RoundedTextFieldStyle())
                                    .textContentType(.familyName)
                            }
                        }

                        VStack(alignment: .leading, spacing: 6) {
                            Text("Email")
                                .font(.caption)
                                .fontWeight(.medium)
                            TextField("votre@email.com", text: $email)
                                .textFieldStyle(RoundedTextFieldStyle())
                                .textContentType(.emailAddress)
                                .keyboardType(.emailAddress)
                                .autocapitalization(.none)
                        }

                        VStack(alignment: .leading, spacing: 6) {
                            Text("Mot de passe")
                                .font(.caption)
                                .fontWeight(.medium)
                            SecureField("6 caractères minimum", text: $password)
                                .textFieldStyle(RoundedTextFieldStyle())
                                .textContentType(.newPassword)
                        }

                        VStack(alignment: .leading, spacing: 6) {
                            Text("Confirmer le mot de passe")
                                .font(.caption)
                                .fontWeight(.medium)
                            SecureField("Retapez le mot de passe", text: $confirmPassword)
                                .textFieldStyle(RoundedTextFieldStyle())
                                .textContentType(.newPassword)
                        }

                        if let error = localError ?? authManager.error {
                            Text(error)
                                .font(.caption)
                                .foregroundColor(.red)
                                .padding(.horizontal)
                        }

                        Button(action: register) {
                            HStack {
                                if authManager.isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Text("Créer mon compte")
                                        .fontWeight(.semibold)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                LinearGradient(
                                    colors: isFormValid ? [.orange, .brown] : [.gray, .gray],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .disabled(authManager.isLoading || !isFormValid)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.1), radius: 10, x: 0, y: 5)
                    )
                    .padding(.horizontal)

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

    private var isFormValid: Bool {
        !email.isEmpty &&
        !firstname.isEmpty &&
        !lastname.isEmpty &&
        password.count >= 6 &&
        password == confirmPassword
    }

    private func register() {
        localError = nil

        guard password == confirmPassword else {
            localError = "Les mots de passe ne correspondent pas"
            return
        }

        guard password.count >= 6 else {
            localError = "Le mot de passe doit contenir au moins 6 caractères"
            return
        }

        Task {
            let success = await authManager.register(
                email: email,
                firstname: firstname,
                lastname: lastname,
                password: password
            )
            if success {
                dismiss()
            }
        }
    }
}

#Preview {
    RegisterView()
        .environmentObject(AuthManager())
}
