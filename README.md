# AliasWrapper

Yeah.
Probably not very useful on GNU/Linux envs, or even any environment different than Windows.
##### This thing allows you to have autosaving command aliases. Period.


## IMPORTANT NOTES
* Implementation is done using... Bad practices. This is not a replacement for your shell (yet). Please use with caution.
* DO NOT BLAME ME IF YOU USE THIS IN A CHAIN OR SOMETHING IMPORTANT AND IT BREAKS THINGS.
* You can use shell commands and execute things by putting `!` before anything. THIS WRAPPER DOES NOT CHECK YOUR PATH YET.


## Things to do
* Cleanup.
* Testing.
* Change internal system to have a shell subprocess instead of shouting system calls.


## How to use
1. Open with your favourite python(3) version.
2. Type `help`
3. Add aliases
4. ??
5. Profit!

## Available commands
* cat
* ls (partially implemented)
* cd
* Execute programs in the system PATH, for example `javac Main.java`