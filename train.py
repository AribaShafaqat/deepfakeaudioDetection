import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from utills import AudioDataset
import matplotlib.pyplot as plt

# DeepSonar-like CNN model
class DeepSonarCNN(nn.Module):
    def __init__(self):
        super(DeepSonarCNN, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.cnn(x)
        x = self.classifier(x)
        return x

# Only run the following code when the file is executed directly
if __name__ == "__main__":
    # Parameters
    batch_size = 16
    learning_rate = 0.001
    epochs = 10

    # Dataset
    dataset = AudioDataset()
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=batch_size)

    # Model, Loss, Optimizer
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = DeepSonarCNN().to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Training
    train_losses, val_losses = [], []

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X, y in train_loader:
            X, y = X.to(device), y.float().to(device)
            y = y.unsqueeze(1)

            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        train_losses.append(total_loss / len(train_loader))

        # Validation
        model.eval()
        val_loss = 0
        correct = 0
        with torch.no_grad():
            for X, y in val_loader:
                X, y = X.to(device), y.float().to(device)
                y = y.unsqueeze(1)
                outputs = model(X)
                val_loss += criterion(outputs, y).item()
                preds = (outputs > 0.5).int()
                correct += (preds == y.int()).sum().item()

        val_losses.append(val_loss / len(val_loader))
        accuracy = correct / len(val_set)

        print(f"Epoch {epoch+1}: Train Loss={train_losses[-1]:.4f}, Val Loss={val_losses[-1]:.4f}, Accuracy={accuracy:.4f}")

    # Save model
    torch.save(model.state_dict(), 'models/deep_sonar_model.pth')

    # Optional: Plot loss
    plt.plot(train_losses, label='Train')
    plt.plot(val_losses, label='Validation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

# from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# # Collect all true and predicted labels
# all_preds = []
# all_labels = []

# model.eval()
# with torch.no_grad():
#     for X, y in val_loader:
#         X = X.to(device)
#         outputs = model(X)
#         preds = (outputs > 0.5).int().cpu().numpy().flatten()
#         all_preds.extend(preds)
#         all_labels.extend(y.numpy().flatten())

# # Classification Report
# print("\n📊 Classification Report:")
# print(classification_report(all_labels, all_preds, target_names=["Fake", "Real"]))

# # Confusion Matrix
# cm = confusion_matrix(all_labels, all_preds)
# disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Fake", "Real"])
# disp.plot(cmap='Blues')
# plt.title("Confusion Matrix")
# plt.show()