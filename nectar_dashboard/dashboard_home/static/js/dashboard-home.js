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
        dataType: "text",
        success: function(data) {
          // Is data object empty?
          if(data) {
            try {
              let news_xml = $.parseXML(data) || (() => { throw new Error("Failed to parse XML. Check RSS feed is valid and does not contain special characters.") })();
              // Validate if has news items
              if(!$(news_xml).find("item").length) {
                throw new Error("Invalid RSS feed format: no items found");
              }

              let news_html = "";
              $(news_xml).find("item").each(function() {
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
                      <p class="news-link"><span class="btn btn-link">Read more</span></p>
                    </a>
                  </div>
                `;
              });
              resolve(news_html);
            }
            catch (parseError) {
              reject(parseError);
            }
          }
          else {
            reject("News feed data is empty");
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
              <div class="row-fluid">
                <div class="col-xs-12 col-sm-6 banner-text">
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

  function escapeHtml(value) {
    if (value === null || value === undefined) {
      return "";
    }
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatRfc2822(dateString) {
    if (!dateString) {
      return "";
    }
    var d = new Date(dateString);
    if (isNaN(d.getTime())) {
      return "";
    }
    return d.toString();
  }

  function renderOutages(outages) {
    var $alerts = $("#outage_alerts");
    var outageBaseUrl = $alerts.data("outage-base-url") || "";
    $alerts.empty();

    var topAlerts = "";
    outages.forEach(function(outage) {
      if (outage.severity >= 2 && !outage.end) {
        var alertClass = outage.severity === 2 ? "alert-warning" : "alert-danger";
        topAlerts += `
          <div class="alert ${alertClass} fade in">
            <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
            <i class="fa fa-exclamation-circle fa-2x" style="vertical-align: middle;"></i>&nbsp;&nbsp;${escapeHtml(outage.title)}
            <a href="${escapeHtml(outageBaseUrl + outage.id)}" target="_blank" class="alert-link">View Announcement <i class="fa fa-external-link"></i></a>
          </div>
        `;
      }
    });
    $alerts.html(topAlerts);

    if (!outages.length) {
      return;
    }

    var $list = $("#announcements");
    var listHtml = "";
    outages.forEach(function(outage) {
      var resolvedPrefix = "";
      if (outage.status_display === "Resolved") {
        resolvedPrefix = "(Resolved)&nbsp;";
      } else if (outage.status_display === "Completed") {
        resolvedPrefix = "(Completed)&nbsp;";
      }

      var timesHtml = "";
      var startDate = outage.start ? new Date(outage.start) : null;
      var hasStarted = startDate && !isNaN(startDate.getTime()) && startDate <= new Date();
      if (outage.start) {
        var startSuffix = hasStarted ? "" : " (scheduled)";
        timesHtml += `<strong>Start:</strong> ${escapeHtml(formatRfc2822(outage.start))}${startSuffix}`;
      }
      if (outage.end) {
        timesHtml += ` <strong>End:</strong> ${escapeHtml(formatRfc2822(outage.end))}`;
      } else if (outage.planned_end) {
        timesHtml += ` <strong>End:</strong> ${escapeHtml(formatRfc2822(outage.planned_end))} (scheduled).`;
      }

      listHtml += `
        <li class="d-flex py-4">
          <div class="announcement-severity">
            <img class="severity-dial" src="/static/img/severity${escapeHtml(outage.severity)}.svg" />
          </div>
          <div class="announcement-details pl-4">
            <h5 class="text-uppercase">
              ${resolvedPrefix}${escapeHtml(outage.scheduled_display)} Outage
            </h5>
            <h4>${escapeHtml(outage.title)}</h4>
            <p>
              <strong>Status:</strong> ${escapeHtml(outage.status_display)}
              ${timesHtml}
            </p>
            <a href="${escapeHtml(outageBaseUrl + outage.id)}" target="_blank">View Announcement <i class="fa fa-external-link"></i></a>
          </div>
        </li>
      `;
    });
    $list.html(listHtml);
    $("#announcements_panel").show();
    $("#news_panel").addClass("col-sm-6");
  }

  function renderSecurityRisks(risks) {
    var $alert = $("#security_risks_alert");
    var securityUrl = $alert.data("security-url") || "#";
    if (!risks || !risks.length) {
      $alert.empty();
      return;
    }
    var alertClass = risks.length >= 3 ? "alert-danger" : "alert-warning";
    $alert.html(`
      <div class="alert ${alertClass}">
        <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
        Your project currently has <strong>${risks.length}</strong> security risks requiring action.
        <a href="${escapeHtml(securityUrl)}" class="alert-link">View Security Risks<i class="fa fa-chevron-right ml-2"></i></a>
      </div>
    `);
  }

  /* Public function to fetch and render service outages */
  home.showOutages = function() {
    $.ajax({
      url: "/api/nectar/outages/",
      type: "GET",
      dataType: "json",
      success: function(data) {
        renderOutages((data && data.items) || []);
      },
      error: function(error) {
        console.error("Failed to fetch outages", error);
      }
    });
  };

  /* Public function to fetch and render security risks */
  home.showSecurityRisks = function() {
    $.ajax({
      url: "/api/varroa/security-risks/",
      type: "GET",
      dataType: "json",
      success: function(data) {
        renderSecurityRisks((data && data.items) || []);
      },
      error: function(error) {
        console.error("Failed to fetch security risks", error);
      }
    });
  };

  // Return public functions
  return home;
}());