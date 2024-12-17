handleTooltipChanged(event, tooltip) {
  const iframeType = "bc3-map-iframe-current" === event.id ? "current" : "baseline";
  console.log(`==> En-ROADS received "tooltip-changed" message from BC3 "${iframeType}" map iframe: ${JSON.stringify(tooltip)}`);
  sd(
    "current" === iframeType ? this.baselineMapIFrame : this.currentScenarioMapIFrame,
    { kind: "set-tooltip", lat: tooltip == null ? void 0 : tooltip.lat, lon: tooltip == null ? void 0 : tooltip.lon }
  );
}
