## Requirements

Write a system test suite for each of two different Python programs. Implement black-box testing without the use of test doubles. Use pytest, pytest-describe, and pytest-spec to implement your test cases. 

- For the first test suite, test each of the four methods within the provided MyDB class using black-box system testing. Assume the implementations of the MyDB methods are correct.

    - Do not use test doubles. Instead, invoke the test subject's procedures and manually verify that each anticipated side effect occurs as expected. Take care to set up and tear down each test case as needed to guarantee test reliability.

- For the second test suite, implement black-box system test cases for the SquirrelServer API. Assume the implementation of the SquirrelServer API is correct.

    - Rather than using test doubles to test class methods directly, implement test cases using a simple HTTP client to test each API endpoint as a black-box system test. This should include each of the five core API endpoints, as well as at least ten distinct failure conditions (404 responses).

    - Test all API outputs and side effects: status codes, response headers, response body, records created, records updated, records deleted, etc. Multiple API endpoints may be required for some test cases, e.g. verify a record can be retrieved after being created.

    - In order to accomplish black-box API system testing, a critical dependency of the test suite will be to execute the Python server program when the test runner starts.

    - Set up and tear down each test case as needed to ensure test reliability and consistency. This should include resetting the database file (squirrel_db.db) to a clean state at the start of each test case using a test fixture. Use the provided template database file that contains an empty table ready for testing.

- Continue using describe blocks to appropriately describe components (API methods, failure conditions, etc.). Thoroughly and intentionally plan and design your test cases to achieve full test coverage of the test subjects. Try to maximize the number of test cases and minimize the number of assertions in each test case.

- Your submission will be evaluated according to the quality, variety, coverage, and intentional design of your test cases. You must implement all test cases using black-box system testing. You will be graded according to the completeness and correctness of your test suite.

---

8/10 - test mydb

14/20 - test squirrels

(-5 for not solving the 'theres a server running already problem')

-2 missing edge and boundary cases. 

You can fix these things and I'll give you points back