import pandas as pd

reviews = pd.read_csv("reviews.csv")

positive_reviews = reviews[reviews['pos'] > 0]
negative_reviews = reviews[reviews['neg'] > 0]

print(f"Total reviews: {len(reviews)}")
print(f"Positive reviews: {len(positive_reviews)}")
print(f"Negative reviews: {len(negative_reviews)}")

positive_reviews.to_csv("positive_reviews.csv", index=False)
negative_reviews.to_csv("negative_reviews.csv", index=False)