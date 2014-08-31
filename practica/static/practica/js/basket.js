/* jshint strict:true, asi:true, laxcomma:true, expr:true */
var practica = (function practica_namespace(o, $) {

    "use strict";
    var BasketAdd = function(form, options) {
        //initialize one basket-form
        this.options = $.extend({}, BasketAdd.defaults, options)
        this.form = form
        this.$form = $(form)
        this.options.url || (this.options.url = this.form.action)
        this.is_processing = false
        this.$send_button = $(this.form.send)
        this.$messages = this.$send_button.nextAll(".messages")
        this.init_events()
    }

    BasketAdd.prototype = {
        
        init_events: function() {
            this.$send_button.click(
                $.proxy(function(event) { 
                    this.process(event)
                    event.preventDefault()
                }, this)
            )
        },

        process: function() {
            if (this.is_processing) return 
            this.is_processing = true
            this.toggle()
            this.send()
        },

        toggle: function() {
            if (this.$send_button.hasClass("active")) {
                this.$send_button
                .removeClass("active")
                .addClass("inactive")
                .attr("disabled", "disabled")
            }
            else {
                this.$send_button
                .removeAttr("disabled")
                .removeClass("inactive")
                .addClass("active")
                this.$messages.empty()

            }
        },

        send: function() {
            $.post(
                this.options.url,
                this.$form.serialize()
            )
            .done(
                $.proxy(function(data) { 
                console.log("in done, data is " + data)
                this.render_response(data) 
                }, this)
            )
            .always(
                $.proxy(function() { 
                console.log("in always")
                this.is_processing = false 
                setTimeout($.proxy(this.toggle, this), this.options.toggle_timeout)
                }, this)
            )
            .fail(
                $.proxy(function() { 
                console.log("post request failed")
                    this.form.submit() 
                }, this)
            )
        },
    
        render_response: function(data) {
            var status = data.status
            var body = data.body
            var messages = data.django_messages
            this[status](body, messages)
        },
    
        error: function(body, messages) {
            //rerender form with errors
            this.$form.empty().template(body)
            new BasketAdd(this.form)
        },
    
        OK: function(body, messages) {
            //show "added in your cart"
            for (var m in messages) {
                if (messages[m].message.trim().length) {
                    this.$messages.template(messages[m].message)
                }
            }
            // Send event to refresh basket display
            var event = $.Event("basket_update")
            body.mini_basket && (event.mini_basket = body.mini_basket)
            this.$form.trigger(event)
        },
    }

    BasketAdd.defaults = {
        toggle_timeout: 5000,
    }

    var BasketItem = function(el, options) {
        this.$el = $(el)
        this.$remove = this.$el.find(".remove")
        this.$remove.find("a").click(
            $.proxy(this.remove_item, this))
        this.form = this.$el.closest("form").get(0)
    }

    BasketItem.prototype = {
        remove_item: function(event) {
            event.preventDefault()
            this.$remove.find("input").get(0).value=1
            this.form.submit()
        }
    }



    if (o.init) var _init = o.init
    o.init = function() {
        _init && _init()
        console.log("Basket forms load...")
        $("form.add-to-basket").each(
            function() { new BasketAdd(this) }
        )

    }
    o.BasketAdd = BasketAdd
    o.basket_init = function() {
        $(".goods-in-cart").children().each(
            function(){new BasketItem(this)})
    }
    

    return o

})(practica || {}, jQuery)
