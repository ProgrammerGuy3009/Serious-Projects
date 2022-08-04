<?php 
// This php will handle Login Credentials
$showEror="false";
// This will check if the user has pressed Login
if($_SERVER["REQUEST_METHOD"]=="POST"){
    include '_dbconnect.php'; // This will include the script and connect to the database "poocho"
    // $email = $_POST['loginEmail'];
    $userna = $_POST['loginusername']; // This variable will store Username
    $pass = $_POST['loginPass']; // This variable will store Password
    $sql = "SELECT * FROM `users` WHERE username = '$userna'"; // This will run a SQL query to check if the entered username exists
    $result = mysqli_query($conn, $sql);
    $numRow = mysqli_num_rows($result); // count the number of records fetched
    if($numRow==1){ // If number of records fetched is one and the username and password is correct then session will assign an ID
        $row = mysqli_fetch_assoc($result);
        if(password_verify($pass, $row['user_password'])){ // Password is stored in hash format so this will check the hashed password
            session_start();
            $_SESSION['loggedin'] = true;
            $_SESSION['username'] = $userna;
            $_SESSION['sno'] = $row['sno'];
            header("Location: /forum/index.php"); // This will send the site to homepage along with saved session ID and exit
            exit();
            }
        else{ // If there is some error or password does not match then it will showerror and will not login
            $showEror = "Incorrect Username or Password";
            header("Location: /forum/index.php?loginsuccess=false&error=$showError");
            exit();
        }
    } // This will send the website to homepage without login because the Username does not exixsts
    header("Location: /forum/index.php?loginsuccess=false&error=Incorrect Username or Password");
            exit();
}
?>