users = [{'id': '1', 'superuser': 't', 'useridentifier': 'dataverseAdmin'}, {'id': '2', 'superuser': 't', 'useridentifier': 'tim'}]
users_new = [{'id': '1', 'superuser': 'f', 'useridentifier': 'dataverseAdmin'}, {'id': '2', 'superuser': 'f', 'useridentifier': 'tim'}]

# Create a dictionary where the 'useridentifier' is the key and the entire dictionary is the value
dict1 = {item['useridentifier']: item for item in users}
dict2 = {item['useridentifier']: item for item in users_new}

# Find the differences based on 'superuser' values
differences = []
for key in dict1:
    if key in dict2 and dict1[key]['superuser'] != dict2[key]['superuser']:
        differences.append((key, dict1[key]['superuser'], dict2[key]['superuser']))

print(differences)
# Print the differences
for key, superuser1, superuser2 in differences:
    print(f"Difference for user '{key}':")
    print("In list1:", superuser1)
    print("In list2:", superuser2)

