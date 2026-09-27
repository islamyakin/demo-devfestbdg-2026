open("/app/data/customers.txt", "a").write("hacked,by,ai-agent\n")
print(open("/app/data/customers.txt").read())
