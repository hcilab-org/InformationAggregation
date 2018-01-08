$(function () {
    $("#button").click(function () {
        $("#result").attr("hidden", "true");
        $("#text1").attr("hidden", "true");
        $("#text2").attr("hidden", "true");
        $("#text3").attr("hidden", "true");
        $("#estimate").attr("hidden", "true");
        $("img").attr("hidden", "true");
        $('a[href="#dot"], a[href="#point"], a[href="#confidence"] ,a[href="#probability"]').unbind('click');

        var data = JSON.stringify({
            "val1": parseFloat($("#val1").val()),
            "val2": parseFloat($("#val2").val()),
            "var1": parseFloat($("#var1").val()),
            "var2": parseFloat($("#var2").val())
        });

        $.ajax({
            url: "/submit",
            type: "POST",
            data: data,
            success: function (json) {
                var data = JSON.parse(json);

                $("#point_img_1").attr("src", "../static/img/" + data["point1"]);
                $("#point_img_2").attr("src", "../static/img/" + data["point2"]);
                $("#confidence_img_1").attr("src", "../static/img/" + data["line1"]);
                $("#confidence_img_2").attr("src", "../static/img/" + data["line2"]);
                $("#dot_img_1").attr("src", "../static/img/" + data["dot1"]);
                $("#dot_img_2").attr("src", "../static/img/" + data["dot2"]);
                $("#probability_img_1").attr("src", "../static/img/" + data["dist1"]);
                $("#probability_img_2").attr("src", "../static/img/" + data["dist2"]);
                $("img").removeAttr("hidden");

                $("#result").removeAttr("hidden");
                $(data["paragraph"]).removeAttr("hidden");
                $("#estimate").removeAttr("hidden");

                var dot = $('a[href="#dot"]');
                var point = $('a[href="#point"]');
                dot.click(function () {
                    $("#text3").attr("hidden", "true");
                    $("#estimate").html("The optimal combined value is <span style='color: #0c8b00'>" + data["estimate_optimal"] + "</span >. Using this visualization, we predict that the user will choose <span style='color: #ff0000'>" + data["estimate_chosen_3"] + "</span > instead. That is, there will be an error of " + data["distance_3"] + ".")
                });
                point.click(function () {
                    $("#text3").removeAttr("hidden");
                    $("#estimate").html("The optimal combined value is <span style='color: #0c8b00'>" + data["estimate_optimal"] + "</span >. Using this visualization, we predict that the user will choose <span style='color: #ff0000'>" + data["estimate_chosen_1"] + "</span > instead. That is, there will be an error of " + data["distance_1"] + ".")
                });
                $('a[href="#confidence"]').click(function () {
                    $("#text3").removeAttr("hidden");
                    $("#estimate").html("The optimal combined value is <span style='color: #0c8b00'>" + data["estimate_optimal"] + "</span >. Using this visualization, we predict that the user will choose <span style='color: #ff0000'>" + data["estimate_chosen_2"] + "</span > instead. That is, there will be an error of " + data["distance_2"] + ".")
                });
                $('a[href="#probability"]').click(function () {
                    $("#text3").removeAttr("hidden");
                    $("#estimate").html("The optimal combined value is <span style='color: #0c8b00'>" + data["estimate_optimal"] + "</span >. Using this visualization, we predict that the user will choose <span style='color: #ff0000'>" + data["estimate_chosen_4"] + "</span > instead. That is, there will be an error of " + data["distance_4"] + ".")
                });

                if (data["paragraph"] === "#text2") {
                    dot.tab('show');
                    $("#text3").html("This visualization is not optimal.");
                    dot.click();
                } else {
                    point.tab('show');
                    point.click();
                }
            }
        });
    });
});

