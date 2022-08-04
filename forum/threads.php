<!-- After pressing on the desired category the user will be redirected to this page where he/she can ask or answer the questions asked -->
<!doctype html>
<html lang="en">

    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Poocho Poocho - Coding Forums</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
            integrity="sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor" crossorigin="anonymous">
        <style>
        #p1 {
            background-color: lightgray;
        }

        #p2:hover {
            /* text-decoration: underline; */
            color: green;
        }
        </style>
    </head>

    <body>
        <?php include 'partials/_header.php'; ?> 
        <?php include 'partials/_dbconnect.php'; ?>
        <?php  // This Script will be used to View or Ask the questions asked on this site according to entered category
        $id=$_GET['catid'];
        $sql = "SELECT * FROM `categories` WHERE category_id = $id";
        $result = mysqli_query($conn, $sql);
        while ($row = mysqli_fetch_assoc($result)) {
            $catname = $row['category_name'];
            $catdesc = $row['category_description'];
        }
        ?>
        <?php
        $showAlert=false;
        $method = $_SERVER['REQUEST_METHOD'];
        if($method=='POST'){
            // Insert thread into DB
            $th_title= $_POST['title'];
            $th_desc= $_POST['desc'];
            $th_title= str_replace("<", "&lt;", $th_title);
            $th_title= str_replace(">", "&gt;", $th_title);
            $th_desc= str_replace("<", "&lt;", $th_desc);
            $th_desc= str_replace(">", "&gt;", $th_desc);
            $no = $_POST["sno"];
            $sql = "INSERT INTO `reqs` (`thread_id`, `thread_title`, `thread_desc`, `thread_cat_id`, `thread_user_id`, `timestamp`) VALUES (NULL,'$th_title' ,'$th_desc' , '$id', '$no', current_timestamp())";
            $result = mysqli_query($conn, $sql);
            $showAlert=true;
            if($showAlert){
                echo '<div class="alert alert-success alert-dismissible fade show" role="alert">
                <strong>Success!</strong> Your request has been made please wait for any further solutions.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>';
            }
        }
        ?>

        <!-- fetch all the categories -->
        <div class="container py-3 my-4" style="background-color: #D6D6D6;">
            <div class="jumbotron">
                <h1 class="display-4">Welcome to <?php echo $catname; ?> Forums!</h1>
                <p class="lead"><?php echo $catdesc ?></p>
                <hr class="my-4">
                <p> This is a peer to peer forum. spam / advertising / self-promote is strictly not allowed. Do not post
                    copyright infringing material. Do not post "offensive" posts / links / images. Do not cross post
                    questions. Remain respectful of other members at all times.
                </p>
                <a class="btn btn-success btn-lg" href="#" role="button">Learn more</a>
            </div>
        </div>
        <?php // This Script will check if the user is logged in, only then you will be able to ask questions
if(isset($_SESSION['loggedin']) && $_SESSION['loggedin']==true){
      echo'<div class="container">
            <h1 class="py-2">Start a Discussion</h1>
            <form action="'. $_SERVER['REQUEST_URI'] .'" method="POST">
                <div class="mb-3">
                    <label for="exampleInputEmail1" class="form-label">Problem Title</label>
                    <input type="text" class="form-control" id="title" name="title" aria-describedby="emailHelp">
                    <div id="emailHelp" class="form-text">Keep your title as short and crisp as possible</div>
                </div>
                <div class="mb-3">
                    <label for="exampleFormControlTextarea1" class="form-label">Elaborate your Concern</label>
                    <textarea class="form-control" id="desc" name="desc" rows="3"></textarea>
                    <input type="hidden" name="sno" value="'. $_SESSION["sno"] .'">
                </div>
                <button type="submit" class="btn btn-success mb-4">Submit</button>
            </form>
        </div>';}
else{ // If not logged in then you wont be able start a discussion
    echo'<div class="container">
            <h1 class="py-2">Start a Discussion</h1>
            <h2 class="lead">Login to start a Discussion</h2>
        </div>';
    }      
       echo'<div class="container px-0 mb-5">
            <h1 class="px-2">Browse Questions</h1>';
            // From here you will be able to see the questions and the pagination done on this page
            $id = $_GET['catid'];
            $pg = $_GET['page'];
            // echo $pg;
            $plimit = 10; // Number of Questions per page
            $from = 0;
            $to = $plimit;
            $sql = "SELECT * FROM `reqs` WHERE thread_cat_id=$id"; // To fetch all the questions in accordance with category
            $result = mysqli_query($conn, $sql);
            $numroo = mysqli_num_rows($result); // Count the number of questions
            $pages = $numroo/$plimit;
            $pages = ceil($pages); // Give number of pages which will be required to show all the questions
            $pagelimit = $pages; // Copy number of pages
            $count = 1; // Will tell on which page the user is, By Default user will be at page 1
            // echo $num;
            // echo $pages;
            $noResult = true;
            while($pagelimit<=$pages){ // Loop to only show given number of questions per page
                if($pg == 1){
                    $sq = "SELECT * FROM `reqs` WHERE thread_cat_id=$id order by thread_id DESC LIMIT $from,$to";
                }
                else{
                    $from = $from + ($plimit * ($pg-1));
                    $sq = "SELECT * FROM `reqs` WHERE thread_cat_id=$id order by thread_id DESC LIMIT $from,$to";
                }
                $res = mysqli_query($conn, $sq);
                
                while ($row = mysqli_fetch_assoc($res)){
                $noResult = false;
                $title = $row['thread_title'];
                $desc = $row['thread_desc'];
                $id2 = $row['thread_id'];
                $req_time = $row['timestamp'];
                $userid = $row['thread_user_id'];
                $sql2 = "SELECT `username` FROM `reqs`,`users` WHERE reqs.thread_user_id = users.sno AND thread_user_id = $userid";
                $result2 = mysqli_query($conn, $sql2);
                $row2 = mysqli_fetch_assoc($result2);
                $usern = $row2['username'];
                echo '<div class="media my-3 "id="p1">
                    <img src="materials/userdefault.png" width="70px" class="mr-3" alt="...">
                    <div class="media-body">
                    <!-- image ko side krna hai -->
                        <p class="fw-bold my-0">'. $usern .' at '. $req_time .'</p>
                        <h5 class="mt-0"><a href="req.php?catid='. $id .'&threadid='. $id2 .'&limit=0" style="text-decoration:none;" id="p2">'. $title .'</a></h5>
                        '. $desc .'
                        </div>
                        </div>';
            }

            $pagelimit = $pagelimit+1;
        }
            if($noResult){ // If there are no questions asked in this category then this will run
                echo '<div class="jumbotron jumbotron-fluid mb-5 py-3" style="background-color: #D6D6D6;">
                <div class="container">
                  <p class="display-4">No Questions for this Category</p>
                  <p class="lead">Be the first one to ask a question.</p>
                  </div>
                  </div>';
                } 
            
            else{ // Pagination starts from here
                $cd = $_GET['page'] + 1;
                $dc = $_GET['page'] - 1;
                echo'<div>
                <nav aria-label="...">
                <ul class="pagination justify-content-center">'; 
                if($_GET['page'] == 1){
                echo'<li class="page-item disabled"><a class="page-link">Previous</a></li>';
                // $from = 0; $to = 5;
                }
                else{
                echo'<li class="page-item"><a class="page-link" href="threads.php?catid='. $id .'&page='. $dc .'">Previous</a></li>';
                $from = $from - $plimit;
                $to = $to - $plimit;}
                    while($pages>=$count){
                        echo' <li class="page-item"><a class="page-link" href="threads.php?catid='. $id .'&page='. $count .'">'. $count .'</a></li>';
                    $count = $count+1;}
                if($_GET['page'] == $pages){
                        echo'<li class="page-item disabled"><a class="page-link">Next</a></li>';}
                else{
                        echo'<li class="page-item"><a class="page-link" href="threads.php?catid='. $id .'&page='. $cd .'">Next</a></li>';
                        // $from = $from + $plimit; $to = $to + $plimit;
                    }
            echo'</ul>
            </nav>
        </div>';}
        echo'</div>';
// </li>
// <li class="page-item active" aria-current="page">
// <a class="page-link" href="#">1</a>
// </li>
        ?>
        <?php include 'partials/_footer.php'; ?>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2" crossorigin="anonymous">
        </script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.5/dist/umd/popper.min.js"
            integrity="sha384-Xe+8cL9oJa6tN/veChSP7q+mnSPaj5Bcu9mPX5F5xIGE0DVittaqT5lorf0EI7Vk" crossorigin="anonymous">
        </script>
        <!-- <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.min.js" integrity="sha384-kjU+l4N0Yf4ZOJErLsIcvOU2qSb74wXpOhqTvwVx3OElZRweTnQ6d31fXEoRD1Jy" crossorigin="anonymous"></script> -->
    </body>

</html>