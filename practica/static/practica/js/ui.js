/* jshint strict:true, asi:true, laxcomma:true, expr:true */
var practica = (function practica_namespace(o, $) {

    "use strict";

    // If you're trying to ascertain which transition end event to bind to, you might do something like...
    var transEndEventNames = {
        'WebkitTransition' : 'webkitTransitionEnd',
        'MozTransition'    : 'transitionend',
        'OTransition'      : 'oTransitionEnd',
        'msTransition'     : 'MSTransitionEnd',
        'transition'       : 'transitionend'
    },
    transEndEventName = transEndEventNames[ Modernizr.prefixed('transition') ]

    // Template class
    var Template = function(template, context) {
        if (template) {
            this.template = template
            Mustache.parse(this.template)
        }
        this.context = context || {}

    }

    Template.prototype = {

        load_from_tag: function(template_id) {
            this.template = $("#" + template_id).html()
            try {
            this.Mustache = Mustache
            this.Mustache.parse(this.template)
            }
            catch(e) {
                if (e instanceof ReferenceError) {
                    console.log("Mustache not found")
                    this.Mustache = undefined
                }
                
            }
            return this
        },

        render_as_$: function(context) {
            return $("<div></div>").html(this.render(context))
        },

        render: function(context) {
            $.extend(this.context, context)
            return this.render_context()
        },

        render_context: function() {
            // should be redefined
            return this.Mustache && this.Mustache.render(this.template, this.context)
        }
    }

    $.fn.extend({
        template_from_tag: function(template_id, context) {
            var $this = $(this)
            return $this.each(function(index) {
                var template = new Template().load_from_tag(template_id)
                var html = template.render(context)
                $this.append(html)
            })
        },

        template: function(template, context) {
            var $this = $(this)
            return $this.each(function(index) {
                var html = new Template(template, context).render()
                $this.append(html)
            })
        },
    })

    var LoginForm = function(element, options) {
        //TODO: disable login button on click (from bootstrap disable-on-click)
        this.$element = $(element)
        this.options = $.extend({}, Navigator.defaults, options)
        this.$instance = this.load_instance().hide()
        this.$element.after(this.$instance)
        $(".user>a.trigger", this.$element).click($.proxy(function(event){
            this.open()
            event.preventDefault()
        }, this))
        $(".form-close", this.$instance).click($.proxy(function(event) { 
            this. close()
            event.preventDefault()
        }, this))
    }

    LoginForm.prototype = {
        open: function() {
            this.$instance.show()
        },

        close: function() {
            this.$instance.hide()
        },

        load_instance: function() {
            var template = new Template()
            var $instance = template.load_from_tag("login").render_as_$()
            return $instance
        }
    }

    var Navigator = function(element, options) {
        this.$element = $(element)
        this.$container = this.$element.parents(".nav__container")
        this.options = $.extend({}, Navigator.defaults, options)
        this.prev_offsets = []
        this.current_offset = 0
        this.sliding = false

        //init controls

        var that = this
        this.$container.on(
            "click.navigator",
            ".nav-control",
            function(e){
                e.preventDefault()
                var $this = $(this)
                var action = $this.data("slide")
                that[action]()
            }
        )

        //init gestures
        var gestures = new Hammer(this.$element.get(0))
        gestures.on("panleft", $.proxy(this.next, this))
        gestures.on("panright", $.proxy(this.prev, this))
        //initializing show-all
        this.$container.find(".show-all>a").click(
            $.proxy(function(event) {
            console.log("fire show-all")
            event.preventDefault()
            this.show_all()
        }, this)
        )


        // slide to current item if there is one
        this.check_current_state()


    }
    Navigator.defaults = {
        duration: 600,
        step: 3,
        margin: 5,
        max_items_display: 8,
        transitionClass: "transition",
    }
    Navigator.prototype = {

        show_all: function() {
            this.$element.queue(
                $.proxy(function() {
                this.$element.css({left:0})
                this.$container.addClass("expanded")
            }, this)
            )
        },

        get_next_right: function(step) {
            var container_width = this.$element.closest(".nav__container-inner").width()
            var nav_position = this.$element.position().left
            return this.$element.children("li").filter(function(index){
                var $this = $(this)
                return nav_position + Math.round($this.position().left) + $this.width() > container_width
            }).slice(0, step)
        },
        get_next_left: function(step) {
            var nav_position = this.$element.position().left
            return this.$element.children("li").filter(function(index){
                var $this = $(this)
                return nav_position + Math.round($this.position().left) < 0
            }).slice(-step)
        },
        get_copy_items: function(side, step) {
            if (side == "left") {
                return this.$element.children("li").slice(0, step)
            }
            return this.$element.children("li").slice(-step)
        },
        get_items_length: function($items) {
            var length = 0
            $items.each(function(index) { 
                length += $(this).outerWidth(true)
            })
            return length
        },
        calculate_offset: function($next_items, direction) {
            var el_position = this.$element.position().left
            var container_width = this.$element.closest(".nav__container-inner").width()
            if (direction == "left") {
                var $last_item = $next_items.last()
                var offset = -($last_item.position().left + $last_item.outerWidth(false) + 
                    el_position - container_width) - this.options.margin
            } else if (direction == "right") {
                var $first_item = $next_items.first()
                var offset = -($first_item.position().left + el_position) + this.options.margin
            } else if (direction == "center") {
                var center_position = container_width / 2
                var offset = center_position - $next_items.first().position().left - el_position
            }
            return offset
        },
        next: function() {
            if (!this.$element.queue().length)
                return this.turn("left")
        },
        prev: function() {
            if (!this.$element.queue().length)
                return this.turn("right")
        },
        check_current_state: function() {
            var $current_item = this.$element.children(".current")
            if ($current_item.length)
                this.slide_to($current_item)
        },
        slide_to: function($item) {
            //place some certain slide in the center
            var offset = this.calculate_offset($item, "center")
            var direction = offset > 0 ? "right": "left"
            var opposite = direction == "right" ? "left": "right"
            this.slide(offset)
            this.$element.queue($.proxy(function() {
                var step = Math.floor(this.options.max_items_display/2)
                var $next_items = this["get_next_"+ opposite](step) 
                if ($next_items.length < step) {
                    var $copy_items = this.get_copy_items(direction, step)
                    var copy_items_length = this.get_items_length($copy_items)
                    $next_items = this["add_to_" + opposite]($copy_items, copy_items_length)
                    this["remove_from_" + direction]($copy_items, copy_items_length)
                }
                this.$element.dequeue()
            }, this))
            return this

        },
        turn: function(direction, step) {
            step = step || this.options.step
            var opposite = direction == "right" ? "left": "right"
            var copy_items_length = 0
            var $next_items = this["get_next_"+ opposite](step) 
            if ($next_items.length < step) {
                var $copy_items = this.get_copy_items(direction, step)
                copy_items_length = this.get_items_length($copy_items)
                $next_items = this["add_to_" + opposite]($copy_items, copy_items_length)
            }
            //get offset: find right/leftmost border of next items and calculate difference
            var offset = this.calculate_offset($next_items, direction)
            // shift row 
            this.slide(offset)
            //get rid of copy_items
            if (copy_items_length) 
                this["remove_from_" + direction]($copy_items, copy_items_length)
            return this
        },

        remove_from_left: function($items, items_length) {
            this.$element.queue(function() {
                $(this).css({left: "+=" + items_length})
                $items.remove()
                console.log("Sliding is over")
                $(this).dequeue()
            })
        },
        remove_from_right: function($items) {
            this.$element.queue(function() {
                $items.remove()
                console.log("Sliding is over")
                $(this).dequeue()
            })
        },

        add_to_left: function($items, items_length) {
            this.$element.css({"left": "-=" + items_length})
            return $items.clone().prependTo(this.$element)
        },
        add_to_right: function($items) {
            return $items.clone().appendTo(this.$element)
        },


        slide: function(offset){
            if (offset == 0) return this
            var className = this.options.transitionClass
            if (Modernizr.csstransitions) {
                this.$element.queue(function() {
                    $(this).addClass(className)
                    .one(transEndEventName, function(){
                        $(this).removeClass(className)
                        .dequeue()
                    })
                    .css({left: "+=" + offset})

                })

            } else {
                this.$element.animate({left: "+=" + offset})

            }
            return this

        }
    }


    var Carousel = function (element, options){
        this.$element = $(element)
        if (!this.$element.length) return
            this.options = $.extend({}, Carousel.defaults, options)
        this.init()
    }

    Carousel.defaults = {
        duration: 600,
        interval: 5000,
        offset: 630,
        pause: "hover"

    }

    Carousel.prototype = {

        init: function() {

            //initialize controls
            var that = this
            var $controls = this.$element.parent().find(".carousel-control-container").children()
            $(document).on("click.carousel", ".carousel-control", function(e) {
                var $this = $(this).filter($controls)
                if ($this) {
                    var action = $this.data('slide')
                    console.log(action)
                    that[action]()
                    e.preventDefault()
                }
            })
            this.options.pause == "hover" && this.$element
            .on('mouseenter', $.proxy(this.pause, this))
            .on('mouseleave', $.proxy(this.cycle, this))

            //initialize cycle
            this.cycle()
        }
          , next: function () {
      if (this.sliding) return
          return this.slide('next')
          }

          , prev: function () {
      if (this.sliding) return
          return this.slide('prev')
          }
          , cycle: function() {
      this.interval && clearInterval(this.interval);
      this.interval = setInterval($.proxy(this.next, this), this.options.interval)
      return this

          }
          , pause: function(){
      clearInterval(this.interval)
      return this

          }
          , slide: function(type) {
      var isCycling = this.interval
      isCycling && this.pause()
      var blah = {
          prev: this.$element.find('.prev'),
          next: this.$element.find('.next'),
          active: this.$element.find('.active')
      }
      var $next = blah[type][type]()

      var opposite = type == 'next' ? 'prev' : 'next'
      var fallback  = type == 'next' ? 'first' : 'last'
      var shift_val = type == 'next' ? '-=' : '+='
      shift_val = [shift_val, this.options.offset].join('')
      this.sliding = true

      $next = $next.length ? $next : this.$element.find('li')[fallback]()
      $next.addClass(type+'-'+type)
      var $bleh = $([blah.prev, blah.next, blah.active, $next])
      .map(function(){return this.get()})
      var that = this
      var cleanup = function() {
          $next.removeClass([type, type].join('-')).addClass(type)
          .removeAttr("style")
          blah[type].removeClass(type).addClass('active')
          .removeAttr("style")
          blah.active.removeClass('active').addClass(opposite)
          .removeAttr("style")
          blah[opposite].removeClass(opposite)
          .removeAttr("style")
          that.sliding = false
      }

      if (Modernizr.csstransitions) {
          $bleh.css({left: shift_val})
          this.$element.one(transEndEventName, cleanup)
      }else {
          $bleh.animate({left: shift_val}, this.options.duration, cleanup) 
      }
      isCycling && this.cycle()
      return this
          }
    }


    //Book-grid class

    var BookGrid = function(el, options) {
        //Book grid object
        this.$el = $(el)
        this.$books = this.$el.children().not(".opened")

        this.$opened = function () { return this.$el.children(".opened") }
        this.$all = this.$el.children()
        this.options = $.extend({}, BookGrid.defaults, options)
        this._moving = false

        //Init events
        var that = this
        this.$books.click(function(e) { 
            that.process(this, e)
        })
        $(window).resize(function(e) { that.reposition(this) })

    }

    BookGrid.prototype = {
        get_row_length: function(){
            var that = this
            var current_length = this.$books.filter(function(index) {
                return $(this).position().top == that.$books.first().position().top
            }).length
            var calculated_length = Math.floor(
                this.$el.width() / (
                    this.$books.outerWidth(true) + this.options.book_width_addition))
                    console.log("row_length: " + calculated_length)
                    return calculated_length
        },

        process: function(el, event) {
            console.log("event.target is" + event.target)
            console.log("this is " + this)
            if (this.set_ajah_ref(
                $(event.target).closest("a").data(this.options.BOOK_AJAH_REF))
               ) 
           {
                event.preventDefault()
                this.toggle(el, event) 
            }
        },

        set_ajah_ref: function(ajah_ref) {
            if (ajah_ref) this.ajah_ref = ajah_ref
            return ajah_ref
        },

        place: function ($instance, el, appear_func) {
            // open instance in the upper (or lower) row
            var pos = this.$books.index(el)
            var insert_method = this.options.place_method == "before" ? "insertBefore" : "insertAfter" 
            var corner_pos = this["" + this.options.place_method + "_index"](pos)
            var $corner_el = this.$books.slice(0, corner_pos + 1).last()
            $instance[insert_method]($corner_el)            
            appear_func()
        },

        after_index: function (pos) {
            var ITEMS_IN_ROW = this.get_row_length()
            return pos + ITEMS_IN_ROW - 1 - pos % ITEMS_IN_ROW
        },

        before_index: function(pos) {
            var ITEMS_IN_ROW = this.get_row_length()
            return pos - pos % ITEMS_IN_ROW
        },

        toggle: function(el, event) {
            var $instance = $(el).data("instance") || this.load_instance(el)   
            if ($.contains(document.documentElement, $instance[0])) this.close($instance)
                else this.open($instance, el, event)

        },
        open: function($instance, el, event) {
            //create (or load from cache) the instance of el, position and show it
            $instance.hide()
            this.place($instance, el, function() {$instance.slideToggle()})
            $(el).data("instance", $instance)
        },

        close: function ($instance) {
            $instance.slideToggle(function () {
                $(this).detach()
            })
        },

        load_instance: function(el) {
            var $instance = $('<li class="opened"></li>').text(
                this.options.LOADING_MESSAGE)
            $.get(this.ajah_ref, $.proxy(function(data) {
                $instance.empty().append(data)
                new o.BasketAdd($("form.add-to-basket", $instance).get(0))
                new Tab($(".toggle", $instance).get(0))
                $(".close>a", $instance).click($.proxy(function (event) {
                        this.close($instance)
                        event.preventDefault()
                    }, this))
                }, this))
                
            return $instance

        },

        get_offset: function(pos) {
            var ITEMS_IN_ROW = this.get_row_length()
            var of1 = pos % ITEMS_IN_ROW
            var of2 = of1 - ITEMS_IN_ROW
            return Math.abs(of2) < Math.abs(of1) ? of2: of1
        },

        move: function(el) {
            var $together = this.$books.add(el)
            var pos = $together.index(el)
            var offset = this.get_offset(pos)
            if (offset !== 0) {
                this._moving = true
                console.log(offset)
                var shift = Math.abs(offset) / offset
                for (var i=1; i<=Math.abs(offset); i++) {
                    this.step(el, shift)
                }
            }
            this._moving = false
        },

        step: function(el, step) {
            var $together = this.$books.add(el)
            var pos = $together.index(el)
            var insert_func = step > 0 ? "insertBefore": "insertAfter"
            $(el).queue(function() {
                $together.eq(pos - step).detach()[insert_func]($together.eq(pos + step))
                $(this).dequeue()
            })
        },

        reposition: function(event) {
            var that = this
            if (!this._moving) {
                this.$opened().each(function(index) {
                    that.move(this)
                })
            }
        }


    }

    BookGrid.defaults = {
        place_method: "before",
        book_width_addition: 0,
        BOOK_AJAH_REF: 'ajahRef',
        LOADING_MESSAGE: 'Загрузка...'
    }

    //Basket display at the top
    //should update itself on ajax basket_update events
    var BasketDisplay = function(el, options) {
        this.options = $.extend({}, BasketDisplay.defaults, options)
        this.$el = $(el)
        $(document).on("basket_update", $.proxy(
            function(event) { this.update(event) }, this))
    }

    BasketDisplay.prototype = {

        update: function(event) {
            event.mini_basket && this.$el.html(event.mini_basket)

        },
    }

    BasketDisplay.defaults = {
    }

    var Tab = function(el, options) {
        this.$el = $(el)
        this.$controls = this.$el.find(".toggle-controls")
        this.$tabs = this.$el.find(".toggle-body")
        var that = this
        this.$controls.find("a").click(
            function(event) { 
            that.toggle(this)
            event.preventDefault()
        }
        )
    }

    Tab.prototype = {
        toggle: function(a) {
            var $a = $(a)
            if ($a.parent().hasClass("active")) return
            var toggle_name = $a.data('toggle')
            this.$controls.find("li").removeClass("active")
            this.$controls.find("a[data-toggle=" + toggle_name + "]")
            .parent().addClass("active")
            this.$tabs.find("li").removeClass("active")
            this.$tabs.find("li[data-toggle=" + toggle_name + "]")
            .addClass("active")

            console.log(a, $a.data('toggle'))
        },
    }


    // Initialization
    if (o.init) var _init = o.init
    o.init = function() {
        _init && _init()
        console.log("Navigator load...")
        var navigator = new Navigator($("ul.nav"))
        o.Navigator = navigator
        console.log("Carousel load...")
        var carousel = new Carousel($('.carousel').get())
        console.log("Login form load...")
        var login_form = new LoginForm($(".topbar"))
        console.log("Book grid load...")
        var book_grid = new BookGrid($(".goods"))
        console.log("BasketDisplay load...")
        new BasketDisplay($(".sub__cart>.cart"))

        // init simple events

        $(window).load(function(){ $("body").addClass("loaded") })

    }
    o.Tab = Tab

    return o

})(practica || {}, jQuery)
