import pcg_benchmark 



env = pcg_benchmark.make("loderunnertile-v0")

#print(env.content_space.sample())


content = env.content_space.sample() 

print(content)

info = env.info(content)

print(info) 