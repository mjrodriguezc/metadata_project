import pandas as pd
import os

###### For multiple data frames  ######

### Cleaning the data ###

# Removing the columns determineted by the user
def column_to_remove(column_to_remove,dfs):
    for i, df in enumerate(dfs):
      if column_to_remove in df.columns:
        dfs[i] = df.drop(columns = column_to_remove)
      else:
        print(f"Data frame {i+1} does not have the column:'{column_to_remove}'.")



### Statistics analysis ###
            
# Number fo words           
def number_of_words (row_header, number_of_elements, df,lista):
    count = 0
    for value in number_of_elements:
        
        if count < len(df):
            objeto = df[value][row_header]
            complete_phrase = objeto.to_string()
            phrase = complete_phrase.split()
            phrase.pop(0)
            total_number = len(phrase)
            lista.append(total_number)
            count +=1
        else:
            break
    return lista

#### New function test

header = ['description', 'name', 'description', 'purpose']




# Number of characters
def character_long (row_header, number_of_elements, df, new_list):
    count = 0
    for value in number_of_elements:
        if count < len(df):
            valor = len(df[value][row_header][0])
            new_list.append(valor)
            count +=1
        else:
            break
    return new_list

# Compare list
def compare_list (list1, list2, threshold = 10):
    sum_list1 = sum(list1)
    sum_list2 = sum(list2)
    
    if sum_list1 > sum_list2:
        larget_list = "List 1"
    elif sum_list2 > sum_list1:
        larget_list = "List 2"
    else:
        return "Both list have the same sum values", None
    
    percentage_difference = abs(sum_list1 - sum_list2) / ((sum_list1 + sum_list2) / 2) * 100
    
    if percentage_difference > threshold:
        return f"{larget_list} has significantly larger values", percentage_difference
    
    else:
        return f"{larget_list} has larger values, but the different is not significant", percentage_difference
    



### Simpler but more complete
    
## FUNCTIONS TO PROCESS ONE ENTRY AT THE TIME ##

# COUNT WORDS: Takes the phrase and returns the number of words. 
# It check lenght and spaces

def count_words(phrase):
    lenght = 0
    if len(phrase) > 1 & phrase.isspace() == True:
        lenght = 1
    
    else:
        words = phrase.split()
        lenght = len(words)
    
    return lenght

# COUNT CHARACTERS: Takes the phrase and returns the number of characters.
# It checks if the phrase is empty

def count_characters(phrase):
    lenght = 0
    if len(phrase) < 1:
        lenght = 0
    else:
        lenght = len(phrase)
        
    return lenght