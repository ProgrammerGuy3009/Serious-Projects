<!-- This is the comments page here user will see the comments of the clicked discussions -->
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
        <?php // Here the script to show all the comments start also one can login to post a comment too
            $id = $_GET['threadid'];
            $var = 10;
            $sql = "SELECT * FROM `reqs` WHERE thread_id = $id";
            $result = mysqli_query($conn, $sql);
            while ($row = mysqli_fetch_assoc($result)) {
                $title = $row['thread_title'];
                $desc = $row['thread_desc'];
            }
            $showAlert = false;
            $method = $_SERVER['REQUEST_METHOD'];
            if ($method == 'POST') {
            // Insert comments into DB
            $comment = $_POST['comment'];
            $comment = str_replace("<", "&lt;", $comment);
            $comment = str_replace(">", "&gt;", $comment);
            $sno = $_POST["sno"];
            $sql = "INSERT INTO `comments` (`comment_content`, `thread_id`, `comment_by`, `comment_time`) VALUES ('$comment', '$id', '$sno', current_timestamp())";
            $result = mysqli_query($conn, $sql);
            $showAlert = true;
            if ($showAlert) {
                echo '<div class="alert alert-success alert-dismissible fade show" role="alert">
                    <strong>Success!</strong> Your comment has been added!
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>';
            }
            }
            $id2 = $_GET['catid'];
            $sql5 = "SELECT * FROM `reqs` WHERE thread_cat_id=$id2";
            $result5 = mysqli_query($conn, $sql5);
            while ($row = mysqli_fetch_assoc($result5)) {
                $tid = $row['thread_id'];
                if ($tid == $id) {
                    $userid = $row['thread_user_id'];
                    $sql2 = "SELECT `username` FROM `reqs`,`users` WHERE reqs.thread_user_id = users.sno AND thread_user_id = $userid";
                    $result2 = mysqli_query($conn, $sql2);
                    $row2 = mysqli_fetch_assoc($result2);
                    $usern = $row2['username'];
                    echo '<div class="container py-3 my-4" style="background-color: lightgray;">
                                    <div class="jumbotron">
                                        <h1 class="display-4">' . $title . '</h1>
                                        <hr class="my-4">
                                        <h5 class="my-4">' . $desc . '</h5>
                                        <p>Posted by :- <b>' . $usern . '</b></p>
                                    </div>
                                </div>';
                }
            }
// Check if user is logged in or not
            if (isset($_SESSION['loggedin']) && $_SESSION['loggedin'] == true) {
                echo '<div class="container">
                    <h1 class="py-2">Post a Comment</h1>
                    <form action="' . $_SERVER['REQUEST_URI'] . '" method="POST">
                        <div class="mb-3">
                            <label for="exampleFormControlTextarea1" class="form-label">Type your comment here</label>
                            <textarea class="form-control" id="comment" name="comment" rows="3"></textarea>
                            <input type="hidden" name="sno" value="' . $_SESSION["sno"] . '">
                        </div>
                        <button type="submit" class="btn btn-success mb-4">Post</button>
                    </form>
                </div>';
            } else {
                echo '<div class="container">
                    <h1 class="py-2">Post a Comment</h1>
                    <h2 class="lead">Login to post a Comment</h2>
                </div>';
            }
        ?>

        <div class="container mb-5" id="ques">
            <h1>Discussions</h1>
            <?php
                $sql = "SELECT * FROM `comments` WHERE thread_id=$id order by comment_id DESC";
                $result = mysqli_query($conn, $sql);
                $noResult = true;
                $numr = mysqli_num_rows($result);
                $seal = $numr/$var;
                $seal = ceil($seal);
                // echo $seal;
                $lim = 0;
                $getlimit = $_GET['limit'];
                $from = 0;
                $check = (($getlimit+10)/$var);
                // echo $check;
                // echo $getlimit;
                if($getlimit == 0 && $numr<=10){ // If the number of comments doesnot exceeds the comments per page
                    while ($row = mysqli_fetch_assoc($result)) {
                        $noResult = false;
                        $id = $row['comment_id'];
                        $content = $row['comment_content'];
                        $comment_time = $row['comment_time'];
                        $commentid = $row['comment_by'];
                        $sql2 = "SELECT `username` FROM `comments`,`users` WHERE comments.comment_by = users.sno AND comment_by = $commentid";
                        $result2 = mysqli_query($conn, $sql2);
                        $row2 = mysqli_fetch_assoc($result2);
                        $usern = $row2['username'];
                        echo '<div class="media my-3 "id="p1">
                                <img src="materials/userdefault.png" width="70px" class="mr-3" alt="...">
                                <div class="media-body">
                                    <!-- image ko side krna hai -->
                                    <p class="fw-bold my-0">' . $usern . ' at ' . $comment_time . '</p>
                                    ' . $content . '
                                    </div>
                                    </div>';
                    }
                                

                    if ($noResult) { // if no comments are posted
                        echo '<div class="jumbotron jumbotron-fluid mb-5 py-3" style="background-color: #D6D6D6;">
                        <div class="container">
                            <p class="display-4">No Questions for this Category</p>
                            <p class="lead">Be the first one to ask a question.</p>
                        </div>
                        </div>';
                    }
                }

                elseif($numr>10){ // If number of comments exceed the no of comments per page then load more
                    $noResult = false;
                    if($getlimit >= 0){
                        $to = $getlimit + 10;
                        $sqli = "SELECT * FROM `comments` WHERE thread_id=$id order by comment_id DESC LIMIT $from,$to";
                        $resulting = mysqli_query($conn, $sqli);
                        $numero = mysqli_num_rows($resulting);
                        while ($lim < $numero) {
                            
                            $row = mysqli_fetch_assoc($resulting);
                                    $id = $row['comment_id'];
                                    $content = $row['comment_content'];
                                    $comment_time = $row['comment_time'];
                                    $commentid = $row['comment_by'];
                                    $sql2 = "SELECT `username` FROM `comments`,`users` WHERE comments.comment_by = users.sno AND comment_by = $commentid";
                                    $result2 = mysqli_query($conn, $sql2);
                                    $row2 = mysqli_fetch_assoc($result2);
                                    $usern = $row2['username'];
                                    echo '<div class="media my-3 "id="p1">
                                            <img src="materials/userdefault.png" width="70px" class="mr-3" alt="...">
                                            <div class="media-body">
                                                <!-- image ko side krna hai -->
                                                <p class="fw-bold my-0">' . $usern . ' at ' . $comment_time . '</p>
                                                ' . $content . '
                                            </div>
                                        </div>';
                                
                                $lim = $lim + 1;
                        }
                    }
                    elseif($check>=$seal){ // If all the comments are shown then load less
                        $id = $_GET['catid'];
                        $id2 = $_GET['threadid'];
                        echo '<a role="button" href="req.php?catid='. $id .'&threadid='. $id2 .'&limit=0">Load less</a>';
                    }
                    else{ // if not all are shown then load more
                        $getlimit = $getlimit + $var;
                        $id = $_GET['catid'];
                        $id2 = $_GET['threadid'];
                        echo '<a role="button" href="req.php?catid='. $id .'&threadid='. $id2 .'&limit='. $getlimit .'">Load more</a>';
                    }
                }
            ?>
            
        </div>
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