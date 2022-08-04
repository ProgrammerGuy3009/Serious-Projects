<?php
// This php script is responsible for a responsive navbar
session_start(); // This will start the session with login credentials
include '_dbconnect.php'; // Connect to database
// This will run the navbar script written in HTML
echo '<nav class="navbar navbar-expand-lg navbar-dark bg-dark py-0">
<div class="container-fluid">
    <a class="navbar-brand" href="/forum">Poocho Poocho</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
                <a class="nav-link" aria-current="page" href="/forum">Home</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/forum/about.php">About</a>
                </li>
            <div class="collapse navbar-collapse" id="navbarNavDarkDropdown">
            <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDarkDropdownMenuLink" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                            Categories
                        </a>
                        <ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="navbarDarkDropdownMenuLink">'; 
                        $sql = "SELECT * FROM `categories`"; // This will run a query to select all the categories
                        $result = mysqli_query($conn, $sql);
                        while($row = mysqli_fetch_assoc($result)){ // This will show all the categories in navbar
                            $catnam = $row['category_name'];
                            $cid = $row['category_id'];
                            echo'<li><a class="dropdown-item" href="http://localhost/forum/threads.php?catid='.$cid.'&page=1">'. $catnam .'</a></li>'; // This will redirect you to the clicked category page
                        }
                        echo'</ul>
                    </li>
                </ul>
                </div>
                <li class="nav-item">
                <a class="nav-link" href="/forum/contact.php" tabindex="-1">Contact</a>
                </li>
        </ul>
        <div class="row mx-2">'; 
        if(isset($_SESSION['loggedin']) && $_SESSION['loggedin']==true){ // Check if the user is logged in
            echo'<form class="d-flex my-sm-0" method = "GET" action="search.php">
            <input class="form-control my-2" name="search" type="search" placeholder="Search" aria-label="Search">
            <button class="btn btn-success my-2 mx-2 my-0" type="submit">Search</button>
              <p class="text-light my-0 mx-2">Welcome '. $_SESSION['username'] .'</p>
              <a href="/forum/partials/_logout.php" type="button" class="btn btn-outline-success my-2">Logout</a></form>';
        }
        // Else it will show sign up or login buttons
        else{echo '<form class="form-inline my-2 my-md-0" method = "GET" action="search.php">
                <input class="form-inline pb-2 mt" name="search" type="search" placeholder="Search" text-align: bottom; aria-label="Search">
                <button class="btn btn-success my-2 my-sm-1" type="submit">Search</button>
                <button type="button" class="btn btn-outline-success ml-2" data-bs-toggle="modal" data-bs-target="#loginModal">Login</button>
                <button type="button" class="btn btn-outline-success" data-bs-toggle="modal" data-bs-target="#signupModal">Signup</button>
            </form>';
            }
        echo '
            </div>
            </div>
        </div>
    </nav>';
include 'partials/_loginModal.php'; // Include the script of login modal
include 'partials/_signupModal.php'; // Include the script of sign up modal
// These Conditions will check if you are logged in or signuped or not and will show an alert accordingly
if(isset($_GET['signupsuccess']) && $_GET['signupsuccess'] == "true"){
        echo'<div class="alert alert-success alert-dismissible fade show my-0" role="alert">
        <strong>Success!</strong> Your Account is created.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>';
}
elseif(isset($_GET['signupsuccess']) && $_GET['signupsuccess'] == "false" && $_GET['error'] == "Email already in use"){
    echo'<div class="alert alert-warning alert-dismissible fade show my-0" role="alert">
    <strong>Error!</strong> Email already in use.
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>';
}
elseif(isset($_GET['signupsuccess']) && $_GET['signupsuccess'] == "false" && $_GET['error'] == "Username already in use"){
    echo'<div class="alert alert-warning alert-dismissible fade show my-0" role="alert">
    <strong>Error!</strong> Username already in use.
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>';
}
elseif(isset($_GET['loginsuccess']) && $_GET['loginsuccess'] == "false" && $_GET['error'] == "Incorrect Username or Password"){
    echo'<div class="alert alert-warning alert-dismissible fade show my-0" role="alert">
    <strong>Error!</strong> Incorrect Username or Password.
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>';
}?>