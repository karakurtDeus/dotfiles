local colors_path = vim.fn.expand("~/.config/polybar/colors.ini")
local rice_path = vim.fn.expand("~/.config/bspwm/rice")

local function blend(fg, bg, alpha)
  local function channel(hex, i)
    return tonumber(hex:sub(i, i + 1), 16)
  end
  local function mix(i)
    return math.floor(channel(fg, i) * alpha + channel(bg, i) * (1 - alpha) + 0.5)
  end
  fg = fg:sub(2)
  bg = bg:sub(2)
  return string.format("#%02x%02x%02x", mix(1), mix(3), mix(5))
end

local function hsv(hex)
  local r = tonumber(hex:sub(2, 3), 16) / 255
  local g = tonumber(hex:sub(4, 5), 16) / 255
  local b = tonumber(hex:sub(6, 7), 16) / 255
  local max = math.max(r, g, b)
  local min = math.min(r, g, b)
  local delta = max - min
  local sat = max == 0 and 0 or delta / max
  return sat, max
end

local function read_palette()
  local file = io.open(colors_path, "r")
  if not file then
    return nil
  end
  local colors = {}
  for line in file:lines() do
    local key, value = line:match("^%s*(nvim_[%w_]+)%s*=%s*(#%x%x%x%x%x%x)")
    if key and value then
      colors[key] = value:lower()
    end
  end
  file:close()
  if not colors.nvim_bg or not colors.nvim_fg then
    return nil
  end
  return colors
end

local function hex_of(n)
  return string.format("#%06x", n)
end

local function surfaces(tokyo, bg, fg)
  local flat = {
    tokyo.bg,
    tokyo.bg_dark,
    tokyo.bg_dark1,
    tokyo.bg_popup,
    tokyo.bg_statusline,
    tokyo.bg_sidebar,
    tokyo.bg_float,
    tokyo.black,
  }
  local raised = blend(fg, bg, 0.08)
  local map = {}
  for _, color in ipairs(flat) do
    if type(color) == "string" then
      map[color:lower()] = bg
    end
  end
  for _, color in ipairs({ tokyo.bg_highlight, tokyo.terminal_black, tokyo.bg_visual }) do
    if type(color) == "string" then
      map[color:lower()] = raised
    end
  end
  return map, raised
end

-- Dark, weakly saturated fills are window backgrounds. Accent fills stay Tokyo Night.
local function surface(hex, known, bg, fg, raised)
  local exact = known[hex]
  if exact then
    return exact
  end
  local sat, value = hsv(hex)
  if value < 0.22 and sat < 0.5 then
    return bg
  end
  if value < 0.4 and sat < 0.45 then
    return raised
  end
  return nil
end

local function paint(c, tokyo)
  local bg = c.nvim_bg:lower()
  local fg = c.nvim_fg:lower()
  local plain = tokyo.fg:lower()
  local known, raised = surfaces(tokyo, bg, fg)
  local flags = {
    "bold",
    "italic",
    "underline",
    "undercurl",
    "underdouble",
    "underdotted",
    "underdashed",
    "strikethrough",
    "reverse",
    "standout",
    "nocombine",
    "blend",
  }

  for name, hl in pairs(vim.api.nvim_get_hl(0, {})) do
    if not hl.link then
      local next_hl = {}
      local changed = false
      if type(hl.bg) == "number" then
        local mapped = surface(hex_of(hl.bg), known, bg, fg, raised)
        if mapped then
          next_hl.bg = mapped
          changed = true
        end
      end
      if type(hl.fg) == "number" and hex_of(hl.fg) == plain then
        next_hl.fg = fg
        changed = true
      end
      if changed then
        if next_hl.fg == nil and type(hl.fg) == "number" then
          next_hl.fg = hex_of(hl.fg)
        end
        if next_hl.bg == nil and type(hl.bg) == "number" then
          next_hl.bg = hex_of(hl.bg)
        end
        if type(hl.sp) == "number" then
          next_hl.sp = hex_of(hl.sp)
        end
        for _, key in ipairs(flags) do
          if hl[key] ~= nil then
            next_hl[key] = hl[key]
          end
        end
        vim.api.nvim_set_hl(0, name, next_hl)
      end
    end
  end

  vim.g.terminal_color_0 = bg
  vim.g.terminal_color_7 = fg
end

local apply

local function watch_rice()
  if vim.g.rice_colors_watch then
    return
  end
  local uv = vim.uv or vim.loop
  if not uv or not uv.fs_stat(rice_path) then
    return
  end
  local handle = uv.new_fs_event()
  if not handle then
    return
  end
  local function arm()
    local ok = handle:start(rice_path, {}, function(err)
      if err then
        handle:stop()
        vim.schedule(arm)
        return
      end
      vim.schedule(apply)
    end)
    if not ok then
      vim.g.rice_colors_watch = false
    end
  end
  vim.g.rice_colors_watch = true
  arm()
end

apply = function()
  local ok, tokyonight = pcall(require, "tokyonight")
  local tokyo
  if ok then
    tokyo = tokyonight.load()
  end
  local colors = read_palette()
  if tokyo and colors then
    paint(colors, tokyo)
    vim.g.colors_name = "rice"
  end
  vim.api.nvim_exec_autocmds("ColorScheme", { modeline = false })
  watch_rice()
end

return {
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = apply,
    },
  },
}
