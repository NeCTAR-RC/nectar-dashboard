var dashboardHome = (function() {

  var home = {};

  function addWelcomeEvent() {
    $("#welcome_dismiss").on("click", function() {
      localStorage.setItem("welcomeDismissed", true);
      hideWelcome();
    });
  }
  
  function showWelcome() {
    $("#welcome").show();
  }

  function hideWelcome() {
    $("#welcome").fadeOut();
  }

  /* Private function to get the project usage to date from api request */
  function getUsageTotal() {
    var api_url = "/api/nectar/usage/summary/?detailed=True";
    $.ajax({
      url: api_url,
      type: 'GET',
      success: function(data) {
        // Is data object empty?
        if($.trim(data.data)) {
          //console.log(data);
          $("#su_total").text(data.sum);
        }
        else {
          console.log("Data empty!");
        }
      },
      error: function (error) {
        console.error(error);
      },
    });
  }

  function getNewsData() {
    const RSS_URL = "/dashboard_home/feed";

    return new Promise((resolve, reject) => {

      $.ajax({
        url: RSS_URL,
        type: 'GET',
        dataType: "xml",
        success: function(data) {
          // Is data object empty?
          if(data) {
            //console.log(data);
            let news_html = "";
            $(data).find("item").each(function() {
              var pub_date = new Date($(this).find("pubDate").html());
              var img_url = $(this).find("image url").html() ? $(this).find("image url").html() : "/static/dashboard_home/img/news-thumb.jpg";
              news_html += `
                <div class="news-slide">
                  <a href="${$(this).find("link").html()}" target="_blank">
                    <div class="news-thumbnail">
                      <img src="${img_url}" />
                    </div>
                    <div class="news-content">
                      <h6 class="news-meta">${pub_date.toDateString()}</h6>
                      <h3 class="news-title">${$(this).find("title").html()}</h3>
                    </div>
                    <p class="btn btn-link news-link">Read more <i class="fa fa-chevron-right"></i></p>
                  </a>
                </div>
              `;
            });
            resolve(news_html);
          }
          else {
            reject("Data empty!");
          }
        },
        error: function (error) {
          reject(error);
        }
      });
    });
  }

  home.checkWelcomeStatus = function() {
    if(!localStorage.welcomeDismissed) {
      //console.log("Welcome not dismissed");
      showWelcome();
      addWelcomeEvent();
    }
  };

  home.showGreeting = function(username) {
    var today = new Date();
    var curHour = today.getHours();
    var ending = (!username) ? "!" : " " + username;

    if(curHour < 12) {
      $("#home_greeting").text("Good morning" + ending);
    } else if (curHour < 18) {
      $("#home_greeting").text("Good afternoon" + ending);
    } else {
      $("#home_greeting").text("Good evening" + ending);
    }
  };

  /* Public function to get ARDC news */
  home.showNews = function() {
    getNewsData().then((result) => {
      $("#ardc_news").html(result);
      $('#ardc_news').slick({
        centerMode: true,
        centerPadding: '60px',
        slidesToShow: 3,
        responsive: [
          {
            breakpoint: 1024,
            settings: {
              arrows: false,
              centerMode: true,
              centerPadding: '40px',
              slidesToShow: 1
            }
          },
          {
            breakpoint: 768,
            settings: {
              arrows: false,
              centerMode: true,
              centerPadding: '40px',
              slidesToShow: 3
            }
          },
          {
            breakpoint: 600,
            settings: {
              arrows: false,
              centerMode: true,
              centerPadding: '40px',
              slidesToShow: 1
            }
          }
        ]
      });
    })
    .catch((error) => {
      console.error(error);
    });
  };

  home.showUsage = function() {
    if($("#project_info")) {
      getUsageTotal();
      //getUsageBudget();
    }
  };

  // Return public functions
  return home;
}());