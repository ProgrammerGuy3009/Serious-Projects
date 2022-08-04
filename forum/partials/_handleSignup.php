<?php 
// This php script will handle the Signup
$showEror="false";
if($_SERVER["REQUEST_METHOD"]=="POST"){ // Will check if the user has submitted the username, email and password
    include '_dbconnect.php'; // Connect to database "Poocho"
    // These variables will store the Email, Username, Password and Confirm Password
    $user_email = $_POST['signupEmail'];
    $usernam = $_POST['signupusername'];
    $pass = $_POST['signuppassword'];
    $cpass = $_POST['signupcpassword'];

    $existsql = "SELECT * FROM `users` WHERE user_email = '$user_email'"; // This will run SQL Query and to see if the email already exists
    $result = mysqli_query($conn, $existsql);
    $numRows = mysqli_num_rows($result); // Store the number of records returned of Emails
    $existsql2 = "SELECT * FROM `users` WHERE username = '$usernam'";
    $result4 = mysqli_query($conn, $existsql2);
    $numRows1 = mysqli_num_rows($result4); // Store the number of records returned of Username
    if($numRows>0){
        $showEror = "Email already in use"; // If email exists then this will show error
    }
    if($numRows1>0){
        $showEror = "Username already in use"; // If username exists then this will show error
    }
    else{ // If all goes well then the else condition will run
        if($pass == $cpass){ // Check if password and confirm password entered is same
            $hash = password_hash($pass, PASSWORD_DEFAULT); // Convert the password to hash value
            $sql = "INSERT INTO `users` (`username`,`user_email`, `user_password`, `timestamp`) VALUES ($usernam, '$user_email', '$hash', current_timestamp())"; // Enter the data into database with SQL query
            $result = mysqli_query($conn, $sql);
            if($result){ // If data is successfully entered then account will be created and you will be redirected to homepage
                $showAlert = true; 
                header("Location:/forum/index.php?signupsuccess=true");
                exit();
            }
        }
        else{ // If cpass and pass do not match 
            $showEror = "Passwords do not match";
            
        }
    }
    header("Location:/forum/index.php?signupsuccess=false&error=$showEror"); // If nothing runs
}


?>