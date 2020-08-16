// mediaelement-player
$(function() {
	function deserialize(string) {
	  var result = {};
	  if (string) {
	    var parts = string.split(/&|\?/);
	    for (var i = 0; i < parts.length; i++) {
	      var part = parts[i].split("=");
	      if (part.length === 2)
	        result[decodeURIComponent(part[0])] = decodeURIComponent(part[1]);
	    }
	  }
	  return result;
	}

	(function(strings) {
		strings['en-US'] = {
			'Download File': 'Open Stream in Desktop-Player'
		}
	})(mejs.i18n.locale.strings);

	var feat = ['playpause', 'volume', 'fullscreen'];

	$('video.mejs').mediaelementplayer({
		features: feat,
		enableAutosize: true
	});

	$('audio.mejs').mediaelementplayer({
		features: ['playpause', 'volume', 'current']
	});

	var $player = $('.video-wrap[data-voc-player]');
	if ($player.length > 0) {
		var config = {
			parent: $player.get(0),
			plugins: [],
			baseUrl: '/static/player/voc-player/',
			autoPlay: true,
			poster: $player.data("poster"),
			audioOnly: false,
			preferredAudioLanguage: $player.data("preferred-language"),
			events: {
				onReady: function() {
					var player = this;
					var playback = player.core.getCurrentContainer().playback;
					var params = deserialize(location.href)
					playback.once(Clappr.Events.PLAYBACK_PLAY, function() {});
				}
			}
		}

		// Select source
		config.vocStream = $player.data("stream");
		new VOCPlayer.Player(config);
	}

	$(window).on('load', function() {
		$(window).trigger('resize');
	});
});

// update teaser images
$(function() {
	setInterval(function() {
		$('.rooms .lecture .teaser').each(function() {
			var
				$teaser = $(this),
				$preload = $('<img />'),
				src = $teaser.data('src');

			if(!src) {
				src = $teaser.prop('src');
				$teaser.data('src', src);
			}

			$preload.on('load', function() {
				$teaser.prop('src', $preload.prop('src'));
			}).prop('src', src + '?'+(new Date()).getTime());
		});
	}, 1000*60);
});

// tabs
$(function() {
	// activate tab via hash and default to video
	function setTabToHash() {
		var activeTab = $('.nav-tabs a[href=' + window.location.hash + ']').tab('show');
	}

	// change hash on tab change
	$('.nav-tabs').on('shown.bs.tab', 'a', function (e) {
		window.location.hash = e.target.hash;
	});

	// adjust tabs when hash changes
	$(window).on('hashchange', setTabToHash).trigger('hashchange');
});

