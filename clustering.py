import pandas as pd
import re
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Load the CSV file
df = pd.read_csv('docs_v1.csv')

# Function to remove HTML and DOM tags
def clean_text(text):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    return cleantext

df['text'] = df['text'].fillna('')
# Clean the text column
df['text'] = df['text'].apply(clean_text)

# Extract URL from each document
urls = df['url']

# Store cleaned content in a list
content_list = df['text'].tolist()

# Vectorize the content using TfidfVectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(content_list)

# Calculate WCSS for a range of cluster numbers
# wcss = []
# for i in range(1, 20):  # Change the range according to your requirement
#     kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
#     kmeans.fit(X)
#     wcss.append(kmeans.inertia_)
#     print("Clusters = ",i)
#     print(kmeans.inertia_)

# # Plot the elbow method graph
# plt.plot(range(1, 20), wcss)
# plt.title('Elbow Method')
# plt.xlabel('Number of Clusters')
# plt.ylabel('WCSS')
# plt.savefig('elbow_method_plot.png')
# plt.show()

kmeans = KMeans(n_clusters=9)
kmeans.fit(X)
clusters = kmeans.labels_

# Convert clusters and URLs to Pandas series
cluster_series = pd.Series(clusters, name='ClusterNumber')
url_series = pd.Series(urls, name='URL')

# Combine URLs and cluster numbers into a DataFrame
results_df = pd.concat([url_series, cluster_series], axis=1)

# Store results in a text file
results_df.to_csv('cluster_results.txt', sep=',', index=False)

print("Cluster results saved to cluster_results.txt")