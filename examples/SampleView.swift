import SwiftUI

struct ContentView: View {
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack {
                Text("Hello, SwiftUI!")
                    .padding()
                
                Button("Dismiss") {
                    presentationMode.wrappedValue.dismiss()
                }
            }
            .navigationBarTitle("My App", displayMode: .inline)
            .navigationBarItems(trailing: Button("Done") {
                // Action
            })
            .edgesIgnoringSafeArea(.all)
        }
    }
}

struct DetailView: View {
    var body: some View {
        Text("Detail")
            .navigationBarTitle("Details")
    }
}
