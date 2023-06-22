import numpy as np
from scipy.linalg import eigh

class PCA:
    """Principal Component Analysis.
    """
    def __init__(self, n_components):
        """Constructor of the PCA class.

        Parameters:
        ===========
        n_components: int
            The number of dimensions for the transformed data.
            Must be less than or equal to n_features.
        """
        self.n_components = n_components
        self._fit_instance = False
    
    def _flip_eigenvectors(self, eigenvectors):
        """Enforce determinism by changing the signs of the eigenvectors.
        """
        max_abs_cols = np.argmax(np.abs(eigenvectors), axis=0)
        signs = np.sign(eigenvectors[max_abs_cols, range(eigenvectors.shape[1])])
        return eigenvectors*signs
    
    def _sort_eigen(self, eigenvalues, eigenvectors):
        """Sort eigenvalues in descending order and their corresponding eigenvectors.
        """
        indices = eigenvalues.argsort()[::-1]
        return eigenvalues[indices], eigenvectors[:, indices]
    
    def fit(self, X):
        """Compute eigenvectors to transform data later

        Parameters:
        ===========
        X: np.array of shape [n_examples, n_features]
            The data matrix
        
        Returns:
        ===========
        None
        """
        # Fit the mean of the data and center it
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean

        # Compute covariance matrix
        cov_mat = np.matmul(X_centered.T, X_centered)/(len(X_centered) - 1)

        # Compute eigenvalues, eigenvectors and sort them
        eigenvalues, eigenvectors = eigh(cov_mat)
        self.eigenvalues, self.eigenvectors = self._sort_eigen(eigenvalues, eigenvectors)

        # Get the explained variance rations
        self.explained_variance_ratio = self.eigenvalues/np.sum(self.eigenvalues)
        
        # Enforce determinism by flipping the eigenvectors
        self.eigenvectors = self._flip_eigenvectors(self.eigenvectors)[:, :self.n_components]

        self._fit_instance = True

    def transform(self, X):
        """Project the data in the directions of the eigenvectors.

        Parameters:
        ===========
        X: np.array of shape [n_examples, n_features]
            The data matrix
        
        Returns:
        ===========
        pcs: np.array[n_examples, n_components]
            The new, uncorrelated features from PCA.
        """
        if not self._fit_instance:
            raise Exception("PCA must be fitted to the data first! Call fit()")
       
        X_centered = X - self.mean
        return np.dot(X_centered, self.eigenvectors)
    
    def fit_transform(self, X):
       """Fits PCA and transforms the data.
       """
       self.fit(X)
       return self.transform(X)



