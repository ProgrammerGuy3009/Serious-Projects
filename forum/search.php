<!-- This page is simply to search discussions and questions across the site -->
<!doctype html>
<html lang="en">

    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Poocho Poocho - Coding Forums</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
            integrity="sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor" crossorigin="anonymous">
        <style>
        #maincontainer {
            /* background-color: lightgray; */
            min-height: 100vh;
        }
        </style>
    </head>

    <body>
        <?php include 'partials/_header.php'; 
         include 'partials/_dbconnect.php'; 
         ?>

        <!-- Search results -->
        <div class="container my-3" id="maincontainer">
            <h1 class="text-center">Search results for <em>"<?php echo $_GET['search']?>"</em></h1>
            <?php
            // $id = $_GET['catid'];
            // echo $id;
            $serch = $_GET["search"];
            $sql = "SELECT * FROM reqs WHERE MATCH (thread_title, thread_desc) against ('$serch')";
            $result = mysqli_query($conn, $sql);
            $numr = mysqli_num_rows($result);
            while($row = mysqli_fetch_assoc($result)){
                $title = $row['thread_title'];
                $desc = $row['thread_desc'];
                $thid = $row['thread_id'];
                $thcid = $row['thread_cat_id'];
                $url = "req.php?catid=$thcid&threadid=$thid";
                echo'<div class="result mx-2 px-2 my-3" style="background-color: #D6D6D6;">
                            <h3><a href="'. $url .'" class="text-dark">'. $title .'</a></h3>
                            <p class="mb-3">'. $desc .'</p>
                    </div>';
                }
                if($numr==0){
                    echo'<div class="jumbotron jumbotron-fluid mb-5 py-3" style="background-color: #D6D6D6;">
                    <div class="container">
                        <p class="display-4">No Results Found</p>
                        <p class="lead">Suggestions: <ul>
                        <li>Make sure that all words are spelled correctly.</li>
                        <li>Try different keywords.</li>
                        <li>Try more general keywords.</li>
                        <li>Try fewer keywords.</li></ul>
                        </p>
                    </div>
                    </div>';
                }
         ?>

        </div>
        <!-- Pagination lagana hai -->

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