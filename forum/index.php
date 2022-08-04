<!-- This is the main Home page of our site and here will be what the users will see about the site -->
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

        #p2 {
            margin: 5px 5px 5px 40px;
        }

        #p3:hover {
            color: green;
        }
        </style>
    </head>

    <body>
        <?php include 'partials/_header.php'; // To include navbar and connect to database
         include 'partials/_dbconnect.php'; ?> 
        <!-- Cards start from here, basic designing here-->
        <div id="carouselExampleFade" class="carousel slide carousel-fade bg-dark" data-bs-ride="carousel">
            <div class="carousel-inner">
                <div class="carousel-item active">
                    <img src="/forum/materials/slide-1.jpg" class="d-block w-100" alt="...">
                </div>
                <div class="carousel-item">
                    <img src="/forum/materials/slide-2.jpg" class="d-block w-100" alt="...">
                </div>
                <div class="carousel-item">
                    <img src="/forum/materials/s-3.jpg" class="d-block w-100" alt="...">
                </div>
            </div>
            <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleFade"
                data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
            </button>
            <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleFade"
                data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
            </button>
        </div>
        <h2 class="text-center mt-1 mb-3" id="p1">Poocho-Browse Categories</h2>
        <!-- fetch all the categories -->
        <div class="container my-4">
            <div class="row my-4">
                <?php // This script will list down all the categories in card format, one can click on it to view inside the category
            $sql = "SELECT * FROM `categories`";
            $result = mysqli_query($conn, $sql);
            while ($row = mysqli_fetch_assoc($result)) {
                $id = $row['category_id'];
                $cat = $row['category_name'];
                echo '<div class="col-md-4 my-2">
                    <div class="card" style="width: 18rem;" id="p2">
                        <img src="/forum/materials/' . $cat . '.jpg" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title"><a href="threads.php?catid=' . $id . 'page=1" style="text-decoration:none;" id="p3">' . $cat . '</a></h5>
                            <p class="card-text">' . substr($row['category_description'], 0, 90) . '...</p>
                            <a href="threads.php?catid=' . $id . '&page=1" class="btn btn-success">View Threads</a>
                        </div>
                    </div>
                  </div>';
            }
            ?>
            </div>
        </div>
<!-- Includes Footer -->
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