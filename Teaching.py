

x = 1 # x is a variable set to 1

y = 2 # y is a variable set to 2

z = x + y # z is a variable set to the sum of x and y

print(z) # print the value of z

# The output of this code is 3

user_input = input("Enter a number: ") # user_input is a variable set to the value entered by the user
user_input = int(user_input) # String input is converted to an integer(a number)


print("You entered: " + str(user_input)) # print the value of user_input by converting it back to a string

if user_input > 10: # if the value of user_input is greater than 10
    print("The number you entered is greater than 10.") # print this message
else:
    print("The number you entered is less than or equal to 10.")

for i in range(5): # repeat the following code 5 times
    print(i) # print the value of i
    # i is just a placeholder variable that takes on the values 0, 1, 2, 3, and 4
    # it could be anything you want, but i is just the common variable used short for index


list = [1, 2, 3, 4, 5] # list is a variable set to a list of numbers

print(list) # print the entire list

print(list[2]) # print the value at index 2 of the list

# Remember lists start from 0 so the value at index 2 is the number 3

for i in range(len(list)): # repeat the following code for each index in the list
    print(list[i]) # print the value at the current index

# The output of this code is:
# 1
# 2
# 3
# 4
# 5

def add(x, y): # define a function called add that takes two parameters x and y
    return x + y # return the sum of x and y


input_1 = int(input("Enter a number: ")) # input_1 is a variable set to the value entered by the user
input_2 = int(input("Enter another number: ")) # input_2 is a variable set to the value entered by the user

# Both of these are converted to integers because the input function returns a string

condition_1 = True

if condition_1: # This is the same as (if condition_1 == True) or (if condition_1 is True)
    print("This is true")

else:
    print("This is false")


condition_2 = False
if condition_2: # This is the same as (if condition_2 == True) or (if condition_2 is True)
    print("This is true")

else:
    print("This is false")

if not condition_2: # This is the same as (if condition_2 == False) or (if condition_2 is False)
    print("hello")
