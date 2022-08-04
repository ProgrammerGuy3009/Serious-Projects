<?php 
// This short script will log you out as well clean your login credentials so you will have to login again
session_start();
session_destroy();
header("Location: /forum");
?>