import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hey There! My name is Ronak"
tokens = enc.encode(text)
print("enc Token", tokens)

detokens = enc.decode([25216, 3274, 0, 3673, 1308, 382, 22848, 422])
print("denc Token", detokens)