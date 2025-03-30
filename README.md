# BackEnd Application. CRUD/JWT/Caching (FastAPI)

## Overview
This nice test project which gonna be CRUD/Auth template in FastAPI - is a back-end base application developed 
using Python and FastAPI, following the MVC design pattern. 
The application interfaces with a MySQL database using SQLAlchemy for ORM and implements field validation 
and dependency injection as needed.

### Features
* MVC Design Pattern: The application is structured into three levels for routing, business logic, and database calls.
* SQLAlchemy ORM: Interfaces with a MySQL database. Database local SQLite.
* Field Validation: Extensive type validation using Pydantic models.
* Dependency Injection: Used for various functionalities including token authentication.
* Token-Based Authentication: Implemented for secure access to endpoints.
* In-Memory Caching: Used for caching responses for up to 5 minutes.

### Endpoints
#### Signup Endpoint
* Description: Accepts email and password, returns a token (JWT or randomly generated string).
* Method: POST
* Path: /auth/signup
#### Login Endpoint
* Description: Accepts email and password, returns a token upon successful login; error response if login fails.
* Method: POST
* Path: /auth/login
#### AddPost Endpoint
* Description: Accepts text and a token for authentication, validates payload size (limit to 1 MB), saves the post in memory, returning postID. Returns an error for invalid or missing token.
* Method: POST
* Path: /posts/post
* Dependencies: Token authentication, payload size validation.
#### GetPosts Endpoint
* Description: Requires a token for authentication, returns all user's posts, implements response caching for up to 5 minutes for the same user. Returns an error for invalid or missing token.
* Method: GET
* Path: /posts
* Dependencies: Token authentication, response caching.
#### PutPost Endpoint
* Description: Accepts postID, text, and a token for authentication, updates the corresponding post in memory. Returns an error for invalid or missing token.
* Method: PUT
* Path: /posts/post/{post_id}
* Dependencies: Token authentication, payload size validation.
#### DeletePost Endpoint
* Description: Accepts postID and a token for authentication, deletes the corresponding post from memory. Returns an error for invalid or missing token.
* Method: DELETE
* Path: /posts/post/{post_id}
* Dependencies: Token authentication.

### Task status:
* ✅ Efficiency: Ensure all functions and dependencies run efficiently, minimizing database calls. 
* ✅ Token-Based Authentication: Utilized for "AddPost" and "GetPosts" endpoints.
* ✅ Request Validation: Implemented for "AddPost" endpoint to ensure payload does not exceed 1 MB.
* ✅ In-Memory Caching: Implemented for "GetPosts" endpoint to cache data for up to 5 minutes.
* ✅ Documentation: In Code comprehensive documentation and comments for each function explaining the purpose and functionality of the code.

