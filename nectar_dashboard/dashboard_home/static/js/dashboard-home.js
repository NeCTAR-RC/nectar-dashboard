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

  /* Private function to get return the bootstrap button class for the associated ardc colour */
  function getButtonClass(ardc_color) {
    let button_class = "";
    switch(ardc_color) {
      case "blue":
        button_class = "btn-primary";
        break;
      case "pink":
        button_class = "btn-primary";
        break;
      case "orange":
        button_class = "btn-primary";
        break;
      case "purple":
        button_class = "btn-primary";
        break;
      default:
        button_class = "btn-default";
    }
    return button_class;
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

  function getBannerData() {
    const BANNER_URL = "https://object-store.rc.nectar.org.au/v1/AUTH_2f6f7e75fc0f453d9c127b490b02e9e3/dashboard-featured-banner/banner.json";

    return new Promise((resolve, reject) => {
      $.ajax({
        url: BANNER_URL,
        type: 'GET',
        dataType: 'JSON',
        cache: false,
        success: function(json_data) {
          // Is json object empty?
          if(json_data[0]) {
            // Return the first item banner data
            resolve(json_data[0]);
          }
          else {
            reject("Data empty!");
          }
        },
        error: function(error) {
          reject(error);
        },
      });
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
        slidesToShow: 5,
        responsive: [
          {
            breakpoint: 2000,
            settings: {
              arrows: false,
              centerMode: true,
              centerPadding: '40px',
              slidesToShow: 3
            }
          },
          {
            breakpoint: 1600,
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

  /* Public function to get ARDC news */
  home.showBanner = function() {
    getBannerData().then((result) => {
      let bannerDiv = $(`<div class="row">
        <div class="col-xs-12">
          <div id="home_featured_banner" class="panel panel-default panel-bg-image" style="background-image: linear-gradient(45deg, rgba(0,0,0,0.3), rgba(0, 0, 0, 0)), url(${result.bg_image});">
            <div class="panel-body py-5">
              <div class="row">
                <div class="col-xs-12 col-sm-6 col-lg-4 banner-text">
                  <h2 class="banner-title h1">${result.title}</h2>
                  <h4 class="banner-subtitle">${result.subtitle}</h4>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>`);

      if(result.info) {
        var infoHtml = `<h5 class="banner-info">${result.info}</h5>`;
        bannerDiv.find(".banner-text").append($(infoHtml));
      }
      if(result.button1) {
        var color = getButtonClass(result.button1.color);
        var buttonHtml = `<a class="banner-btn btn ${color} btn-lg" href="${result.button1.link}">${result.button1.text}</a>`;
        bannerDiv.find(".banner-text").append($(buttonHtml));
      }
      if(result.button2) {
        var color = getButtonClass(result.button2.color);
        var buttonHtml = `<a class="banner-btn btn ${color} btn-lg ml-1" href="${result.button2.link}">${result.button2.text}</a>`;
        bannerDiv.find(".banner-text").append($(buttonHtml));
      }
      $("#banner").append(bannerDiv);
    })
    .catch((error) => {
      console.error(error);
    });
  };

  /* Public function to get usage for display in panel */
  home.showUsage = function() {
    if($("#project_info")) {
      getUsageTotal();
      //getUsageBudget();
    }
  };

  // Return public functions
  return home;
}());