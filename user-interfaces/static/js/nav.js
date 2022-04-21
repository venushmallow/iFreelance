const createNav = () => {
    let nav = document.querySelector('.navbar');

    nav.innerHTML = `
    <nav class="nav">
    <div class="container">
        <div class="logo">
            <a href="/homepage">
            <img src="../static/img/logo.png" class="logo" alt="">
            </a>
        </div>
        <div id="mainListDiv" class="main_list">
            <ul class="navlinks">
                <li><a href="/jobpage">Find Services</a></li>
                <li><a href="/buyer_page">Buyer View</a></li>
                <li><a href="/seller_page">Seller View</a></li>
                <li><a href="#">About</a></li>
                <li><a href="#">{{g.user.user_email}} {{g.user.account_id}}</a></li>
            </ul>
        </div>
        <span class="navTrigger">
            <i></i>
            <i></i>
            <i></i>
        </span>
    </div>
</nav>
    `;
}

createNav();