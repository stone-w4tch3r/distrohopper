from lib.modify_file import DictWrapper, ListWrapper


def test_dict_wrapper():
    # Test 1: Test the set method with a nested dictionary
    dictionary = {"cars": {"car0": {"name": "Toyota", "year": 2000}, "car1": {"name": "BMW", "year": 2001}}}
    modified_dict = DictWrapper(dictionary)["cars"]["car0"]["name"].set("Mercedes")
    expected_dict = {"cars": {"car0": {"name": "Mercedes", "year": 2000}, "car1": {"name": "BMW", "year": 2001}}}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 2: Test the append method with a list
    dictionary = {"cars": ["Toyota", "BMW"]}
    modified_dict = DictWrapper(dictionary)["cars"].append("Mercedes")
    expected_dict = {"cars": ["Toyota", "BMW", "Mercedes"]}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 3: Test the set method with a nested dictionary
    dictionary = {"cars": {"car0": {"name": "Toyota", "year": 2000}, "car1": {"name": "BMW", "year": 2001}}}
    modified_dict = DictWrapper(dictionary)["cars"]["car0"].set({"name": "Mercedes", "year": 2022})
    expected_dict = {"cars": {"car0": {"name": "Mercedes", "year": 2022}, "car1": {"name": "BMW", "year": 2001}}}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 4: Test the set method with a new key
    dictionary = {"cars": {"car0": {"name": "Toyota", "year": 2000}, "car1": {"name": "BMW", "year": 2001}}}
    modified_dict = DictWrapper(dictionary)["cars"]["car2"].set({"name": "Mercedes", "year": 2022})
    expected_dict = {
        "cars": {"car0": {"name": "Toyota", "year": 2000}, "car1": {"name": "BMW", "year": 2001}, "car2": {"name": "Mercedes", "year": 2022}}}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 5: Test the set method with an empty dictionary
    dictionary = {}
    modified_dict = DictWrapper(dictionary)["cars"].set("Toyota")
    expected_dict = {"cars": "Toyota"}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 6: Test the append method with an empty list
    dictionary = {"cars": []}
    modified_dict = DictWrapper(dictionary)["cars"].append("Toyota")
    expected_dict = {"cars": ["Toyota"]}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 7: Test the remove method with a nested dictionary
    dictionary = {"cars": {"car0": {"name": "Toyota", "year": 2000}, "car1": {"name": "BMW", "year": 2001}}}
    modified_dict = DictWrapper(dictionary)["cars"]["car0"].remove()
    expected_dict = {"cars": {"car1": {"name": "BMW", "year": 2001}}}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 8: Test the remove method with a list
    dictionary = {"cars": ["Toyota", "BMW"]}
    modified_dict = DictWrapper(dictionary)["cars"].remove()
    expected_dict = {}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 9: Test the remove method with single value
    dictionary = {"cars": "Toyota"}
    modified_dict = DictWrapper(dictionary)["cars"].remove()
    expected_dict = {}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 10: Test the modify_chained method
    dictionary = {"cars": {"car0": {"name": "Toyota", "year": 2000}, "car1": {"name": "BMW", "year": 2001}}}
    modified_dict = DictWrapper(dictionary).modify_chained(
        [
            lambda x: x["cars"]["car0"]["name"].set("Mercedes"),
            lambda x: x["cars"]["car1"]["name"].set("Audi"),
        ]
    )
    expected_dict = {"cars": {"car0": {"name": "Mercedes", "year": 2000}, "car1": {"name": "Audi", "year": 2001}}}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    # Test 11: Test the modify_chained method with complex operations
    dictionary = {"cars": {"car0": {"name": "Toyota"}}}
    modified_dict = DictWrapper(dictionary).modify_chained(
        [
            lambda x: x["cars"]["car1"].set({"name": "Audi", "year": 2022, "passengers": ["Alice", "Bob"]}),
            lambda x: x["cars"]["car1"]["passengers"].append("Charlie"),
        ]
    )
    expected_dict = {"cars": {"car0": {"name": "Toyota"}, "car1": {"name": "Audi", "year": 2022, "passengers": ["Alice", "Bob", "Charlie"]}}}
    assert modified_dict == expected_dict, f"Expected: {expected_dict}, Got: {modified_dict}"

    print("All DictWrapper tests passed successfully!")


def list_wrapper_tests():
    # Test 1: Test the append method
    lst = [1, 2, 3]
    modified_lst = ListWrapper(lst).append(4)
    expected_lst = [1, 2, 3, 4]
    assert modified_lst == expected_lst, f"Got: {modified_lst}, expected: {expected_lst}"

    # Test 2: Test the set method
    lst = [1, 2, 3]
    modified_lst = ListWrapper(lst)[1].set(5)
    expected_lst = [1, 5, 3]
    assert modified_lst == expected_lst, f"Got: {modified_lst}, expected: {expected_lst}"

    # Test 3: Test the remove method
    lst = [1, 2, 3]
    modified_lst = ListWrapper(lst).remove(1)
    expected_lst = [1, 3]
    assert modified_lst == expected_lst, f"Got: {modified_lst}, expected: {expected_lst}"

    # Test 4: Test the modify_chained method
    lst = [1, 2, 3]
    modified_lst = ListWrapper(lst).modify_chained(
        [
            lambda x: x.append(4),
            lambda x: x[0].set(5),
        ]
    )
    expected_lst = [5, 2, 3, 4]
    assert modified_lst == expected_lst, f"Got: {modified_lst}, expected: {expected_lst}"

    print("All ListWrapper tests passed successfully!")


def main():
    test_dict_wrapper()
    list_wrapper_tests()


main()
