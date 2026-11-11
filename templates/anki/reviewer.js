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
    const state = { host, stage, svg: null, frame: null, space: null };
    state.align = () => {
        if (!state.frame || !state.space || !state.space.isConnected) return;
        const box = state.space.getBoundingClientRect();
        const frame = stage.getBoundingClientRect();
        // Account for client zoom as well as normal resize and scrolling.
        const scale = frame.width / stage.clientWidth || 1;
        Object.assign(state.frame.style, {
            left: (box.left - frame.left) / scale + "px",
            top: (box.top - frame.top) / scale + "px",
            width: box.width / scale + "px",
            height: box.height / scale + "px",
        });
        if (zoomable()) strokeScale();
    };
    state.update = () => {
        const incoming = host.querySelector(".fg-card .fg-map");
        if (!incoming) {
            if (state.space && host.contains(state.space)) return state.align();
            stage.hidden = true;
            stage.replaceChildren();
            state.svg = state.frame = state.space = null;
            return;
        }
        const viewBox = incoming.getAttribute("viewBox").split(/\s+/).map(Number);
        const space = document.createElement("div");
        space.className = "fg-map-space";
        space.style.aspectRatio = viewBox[2] + " / " + viewBox[3];
        space.setAttribute("aria-hidden", "true");
        incoming.replaceWith(space);
        state.space = space;
        state.full = viewBox;
        let sameCard = false;
        if (!state.svg) {
            // The frame clips the map, which zoomable maps draw larger than the frame.
            state.svg = incoming;
            state.frame = document.createElement("div");
            state.frame.className = "fg-map-frame";
            state.frame.append(incoming);
            stage.append(state.frame);
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
            // Revealing a zoomable card keeps the reader's zoom; another card starts unzoomed.
            sameCard =
                current.classList.contains("fg-zoomable") &&
                incoming.classList.contains("fg-zoomable") &&
                current.dataset.targetBox === incoming.dataset.targetBox;
            for (const attribute of ["viewBox", "aria-label", "data-max-zoom", "data-target-box"]) {
                if (attribute === "viewBox" && sameCard) continue;
                const value = incoming.getAttribute(attribute);
                if (value === null) current.removeAttribute(attribute);
                else if (current.getAttribute(attribute) !== value) current.setAttribute(attribute, value);
            }
            current.classList.toggle("fg-zoomable", incoming.classList.contains("fg-zoomable"));
        }
        state.frame.classList.toggle("fg-zoomable-frame", zoomable());
        if (zoomable()) {
            // A highlighted target on a new card ("which street is this?") starts framed on it.
            if (!sameCard) state.view = state.svg.querySelector(".fg-highlight") ? focus() : viewBox;
            state.pending = null;
            render();
            if (sameCard && state.svg.querySelector(".fg-highlight")) state.reveal();
        } else {
            Object.assign(state.svg.style, { left: "", top: "", width: "", height: "", transform: "", fontSize: "" });
        }
        // Every new face starts on its primary map; the alternate shows only while pressed.
        const alternate = incoming.classList.contains("fg-has-alternate");
        state.svg.classList.toggle("fg-has-alternate", alternate);
        state.svg.classList.toggle("tappable", alternate || incoming.classList.contains("fg-zoomable"));
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
    // Zoomable maps: drag to pan, pinch or wheel to zoom, within the view and its maximum zoom.
    // Redrawing thousands of streets on every finger move lags on phones. During a gesture
    // the already drawn image only moves and scales (a cheap CSS transform); the map is
    // redrawn sharp when the gesture ends, or earlier if the image no longer covers the view.
    // It is drawn with a margin around the view so that short pans and zoom-outs stay covered.
    const OVERSCAN = 0.5;
    const zoomable = () => state.svg && state.svg.classList.contains("fg-zoomable");
    const view = () => state.pending || state.view;
    const render = () => {
        const [x, y, w, h] = state.view;
        state.rendered = [x - w * OVERSCAN, y - h * OVERSCAN, w * (1 + 2 * OVERSCAN), h * (1 + 2 * OVERSCAN)];
        state.svg.setAttribute("viewBox", state.rendered.map(v => +v.toFixed(2)).join(" "));
        const offset = -OVERSCAN * 100 + "%";
        const size = (1 + 2 * OVERSCAN) * 100 + "%";
        Object.assign(state.svg.style, { left: offset, top: offset, width: size, height: size, transform: "" });
        strokeScale();
    };
    // Street widths are in em: one em is 100 screen pixels in map units at the drawn zoom,
    // large enough to stay above the minimum font size some WebViews enforce.
    const strokeScale = () => {
        const width = state.frame.clientWidth;
        if (width) state.svg.style.fontSize = (100 * state.view[2]) / width + "px";
    };
    const place = () => {
        state.frameRequest = 0;
        if (!state.pending) return;
        const [px, py, pw, ph] = state.pending;
        const [rx, ry] = state.rendered;
        const width = state.frame.clientWidth;
        const height = state.frame.clientHeight;
        const tx = ((rx - px) / pw + OVERSCAN) * width;
        const ty = ((ry - py) / ph + OVERSCAN) * height;
        state.svg.style.transform = `translate(${tx}px, ${ty}px) scale(${state.view[2] / pw})`;
    };
    const commit = () => {
        cancelAnimationFrame(state.frameRequest);
        state.frameRequest = 0;
        if (state.pending) state.view = state.pending;
        state.pending = null;
        render();
    };
    const covered = ([x, y, w, h]) => {
        const [fx, fy, fw, fh] = state.full;
        const [rx, ry, rw, rh] = state.rendered;
        // Beyond the map edges there is nothing to draw; past 2x the image would blur.
        return (
            state.view[2] / w <= 2 &&
            Math.max(x, fx) >= rx &&
            Math.max(y, fy) >= ry &&
            Math.min(x + w, fx + fw) <= rx + rw &&
            Math.min(y + h, fy + fh) <= ry + rh
        );
    };
    const show = box => {
        state.pending = box;
        if (!covered(box)) return commit();
        if (!state.frameRequest) state.frameRequest = requestAnimationFrame(place);
    };
    const fit = ([x, y, w, h]) => {
        const [fx, fy, fw, fh] = state.full;
        const width = Math.min(Math.max(w, fw / (+state.svg.dataset.maxZoom || 1)), fw);
        const height = (width * fh) / fw;
        const cx = Math.min(Math.max(x + w / 2, fx + width / 2), fx + fw - width / 2);
        const cy = Math.min(Math.max(y + h / 2, fy + height / 2), fy + fh - height / 2);
        return [cx - width / 2, cy - height / 2, width, height];
    };
    // The frame is never transformed, so its box maps the visible view to the screen.
    const frameBox = () => state.gestureBox || state.frame.getBoundingClientRect();
    const toMap = (clientX, clientY) => {
        const rect = frameBox();
        const [x, y, w, h] = view();
        return [x + ((clientX - rect.left) / rect.width) * w, y + ((clientY - rect.top) / rect.height) * h];
    };
    const zoomAt = ([px, py], factor) => {
        const [x, y, w, h] = view();
        const [, , fw] = state.full;
        const width = Math.min(Math.max(w / factor, fw / (+state.svg.dataset.maxZoom || 1)), fw);
        const scale = width / w;
        show(fit([px - (px - x) * scale, py - (py - y) * scale, width, h * scale]));
    };
    // Three times the target, at least a sixth of the map, so the area stays recognisable.
    const focus = () => {
        const [tx, ty, tw, th] = state.svg.dataset.targetBox.split(" ").map(Number);
        const side = Math.min(state.full[2], Math.max(Math.max(tw, th) * 3, state.full[2] / 6));
        return fit([tx + tw / 2 - side / 2, ty + th / 2 - side / 2, side, (side * state.full[3]) / state.full[2]]);
    };
    state.reveal = () => {
        const [tx, ty, tw, th] = state.svg.dataset.targetBox.split(" ").map(Number);
        const [x, y, w, h] = state.view;
        if (tx >= x && ty >= y && tx + tw <= x + w && ty + th <= y + h) return;
        // Zoom out just enough to show both the street and where the reader was looking.
        const margin = Math.max(tw, th) * 0.15 + state.full[2] / 100;
        const x0 = Math.min(x, tx - margin);
        const y0 = Math.min(y, ty - margin);
        const x1 = Math.max(x + w, tx + tw + margin);
        const y1 = Math.max(y + h, ty + th + margin);
        const width = Math.max(x1 - x0, ((y1 - y0) * state.full[2]) / state.full[3]);
        const height = (width * state.full[3]) / state.full[2];
        const start = [x, y, w, h];
        // Draw the final view once, then animate the transform from the reader's view to it.
        state.view = fit([(x0 + x1 - width) / 2, (y0 + y1 - height) / 2, width, height]);
        render();
        const end = state.view;
        const began = performance.now();
        const step = now => {
            if (state.view !== end || pointers.size) return;
            const t = Math.min((now - began) / 350, 1);
            const ease = 1 - (1 - t) ** 3;
            state.pending = t < 1 ? start.map((v, i) => v + (end[i] - v) * ease) : null;
            if (state.pending) {
                place();
                requestAnimationFrame(step);
            } else state.svg.style.transform = "";
        };
        state.pending = start;
        place();
        requestAnimationFrame(step);
    };
    const pointers = new Map();
    stage.addEventListener("pointerdown", event => {
        if (!zoomable()) return;
        try {
            state.svg.setPointerCapture(event.pointerId);
        } catch (error) {}
        if (!pointers.size) state.gestureBox = state.frame.getBoundingClientRect();
        pointers.set(event.pointerId, [event.clientX, event.clientY]);
        event.preventDefault();
        event.stopPropagation();
    });
    stage.addEventListener("pointermove", event => {
        if (!zoomable() || !pointers.has(event.pointerId)) return;
        const before = [...pointers.values()];
        pointers.set(event.pointerId, [event.clientX, event.clientY]);
        const after = [...pointers.values()];
        const centre = points => points.reduce(([a, b], [x, y]) => [a + x / points.length, b + y / points.length], [0, 0]);
        const [bx, by] = centre(before);
        const [ax, ay] = centre(after);
        if (after.length > 1) {
            const spread = points => Math.hypot(points[0][0] - points[1][0], points[0][1] - points[1][1]);
            zoomAt(toMap(bx, by), spread(after) / (spread(before) || 1));
        }
        const rect = frameBox();
        const [x, y, w, h] = view();
        show(fit([x - ((ax - bx) / rect.width) * w, y - ((ay - by) / rect.height) * h, w, h]));
        event.stopPropagation();
    });
    for (const name of ["pointerup", "pointercancel"]) {
        stage.addEventListener(name, event => {
            if (!pointers.delete(event.pointerId) || pointers.size) return;
            state.gestureBox = null;
            if (zoomable() && state.pending) commit();
        });
    }
    stage.addEventListener(
        "wheel",
        event => {
            if (!zoomable()) return;
            event.preventDefault();
            zoomAt(toMap(event.clientX, event.clientY), Math.exp(-event.deltaY * 0.002));
            clearTimeout(state.wheelTimer);
            state.wheelTimer = setTimeout(() => state.pending && commit(), 150);
        },
        { passive: false },
    );
    // Presses and drags are not taps: keep them from reaching the client's tap actions.
    stage.addEventListener("click", event => {
        if (state.svg && (state.svg.classList.contains("fg-has-alternate") || zoomable())) {
            event.stopPropagation();
        }
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
