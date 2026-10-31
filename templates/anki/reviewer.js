// Keep the live SVG outside the HTML container replaced by the reviewer.
(() => {
    const host = document.getElementById("qa") || document.getElementById("content");
    if (!host) return;
    const previous = window.frenchGeographyMap;
    if (previous && previous.host === host && previous.stage) {
        previous.update();
        return;
    }
    if (previous) {
        previous.observer.disconnect();
        if (previous.resize) previous.resize.disconnect();
        if (previous.stage) previous.stage.remove();
        window.removeEventListener("resize", previous.align);
        window.removeEventListener("scroll", previous.align);
    }
    const stage = document.createElement("div");
    stage.className = "fg-map-stage";
    document.body.append(stage);
    const state = { host, stage, svg: null, space: null };
    state.align = () => {
        if (!state.svg || !state.space || !state.space.isConnected) return;
        const box = state.space.getBoundingClientRect();
        const frame = stage.getBoundingClientRect();
        // Account for client zoom as well as normal resize and scrolling.
        const scale = frame.width / stage.clientWidth || 1;
        Object.assign(state.svg.style, {
            left: (box.left - frame.left) / scale + "px",
            top: (box.top - frame.top) / scale + "px",
            width: box.width / scale + "px",
            height: box.height / scale + "px",
        });
    };
    state.update = () => {
        const incoming = host.querySelector(".fg-card .fg-map");
        if (!incoming) {
            if (state.space && host.contains(state.space)) return state.align();
            stage.hidden = true;
            stage.replaceChildren();
            state.svg = state.space = null;
            return;
        }
        const viewBox = incoming.getAttribute("viewBox").split(/\s+/).map(Number);
        const space = document.createElement("div");
        space.className = "fg-map-space";
        space.style.aspectRatio = viewBox[2] + " / " + viewBox[3];
        space.setAttribute("aria-hidden", "true");
        incoming.replaceWith(space);
        state.space = space;
        if (!state.svg) {
            state.svg = incoming;
            stage.append(incoming);
        } else {
            const current = state.svg;
            const before = [...current.querySelectorAll(".fg-background")];
            const after = [...incoming.querySelectorAll(".fg-background")];
            if (before.length === after.length) {
                before.forEach((background, i) => {
                    const href = after[i].getAttribute("href");
                    if (background.getAttribute("href") !== href) background.setAttribute("href", href);
                });
                current.querySelectorAll(".fg-highlight").forEach(target => target.remove());
                after.forEach((background, i) => {
                    const target = background.nextElementSibling;
                    if (target && target.classList.contains("fg-highlight")) before[i].after(target);
                });
                current.querySelectorAll(":scope > .fg-alternate").forEach(group => group.remove());
                const alternate = incoming.querySelector(":scope > .fg-alternate");
                if (alternate) current.append(alternate);
            } else {
                // Changing from a single map to a map with an inset, or back.
                current.replaceChildren(...incoming.childNodes);
            }
            for (const attribute of ["viewBox", "aria-label"]) {
                const value = incoming.getAttribute(attribute);
                if (current.getAttribute(attribute) !== value) current.setAttribute(attribute, value);
            }
        }
        // Every new face starts on its primary map; the alternate shows only while pressed.
        const alternate = incoming.classList.contains("fg-has-alternate");
        for (const name of ["fg-has-alternate", "tappable"]) state.svg.classList.toggle(name, alternate);
        state.svg.classList.remove("fg-show-alternate");
        stage.hidden = false;
        state.align();
    };
    const press = shown => event => {
        if (!state.svg || !state.svg.classList.contains("fg-has-alternate")) return;
        // Capture keeps the release even when the finger slides off the map.
        if (shown && event.pointerId !== undefined) {
            try {
                state.svg.setPointerCapture(event.pointerId);
            } catch (error) {}
        }
        if (event.cancelable) event.preventDefault();
        event.stopPropagation();
        state.svg.classList.toggle("fg-show-alternate", shown);
    };
    const [down, up] = window.PointerEvent ? ["pointerdown", "pointerup pointercancel"] : ["touchstart", "touchend touchcancel"];
    stage.addEventListener(down, press(true));
    for (const name of up.split(" ")) stage.addEventListener(name, press(false));
    // The press is not a tap: keep it from reaching the client's tap actions.
    stage.addEventListener("click", event => {
        if (state.svg && state.svg.classList.contains("fg-has-alternate")) event.stopPropagation();
    });
    state.observer = new MutationObserver(state.update);
    state.observer.observe(host, { childList: true, subtree: true });
    if (window.ResizeObserver) {
        state.resize = new ResizeObserver(state.align);
        state.resize.observe(host);
    }
    window.addEventListener("resize", state.align);
    window.addEventListener("scroll", state.align, { passive: true });
    window.frenchGeographyMap = state;
    state.update();
})();
