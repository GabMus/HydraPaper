gnome = import('gnome')
app_id = 'org.gabmus.hydrapaper'

desktop_conf = configuration_data()
desktop_conf.set('bindir', join_paths(prefix, get_option('bindir')))

desktop_file = configure_file(
  input: app_id + '.desktop.in',
  output: app_id + '.desktop',
  #type: 'desktop',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications'),
  configuration: desktop_conf
)

# TODO: Requires GLib 2.52 because of Meson issue
#desktop_service = configure_file(
#  input: app_id + '.service.desktop.in',
#  output: app_id + '.service.desktop',
#  configuration: desktop_conf,
#  install: true,
#  install_dir: pkgdatadir,
#)

# i18n.merge_file(
#   input: desktop_file,
#   output: app_id + '.desktop',
#   type: 'desktop',
#   po_dir: '../po',
#   install: true,
#   install_dir: join_paths(get_option('datadir'), 'applications')
# )
#
# i18n.merge_file(
#   input: app_id + '.appdata.xml.in',
#   output: app_id + '.appdata.xml',
#   po_dir: '../po',
#   install: true,
#   install_dir: join_paths(get_option('datadir'), 'appdata')
# )

dbus_conf = configuration_data()
dbus_conf.set('bindir', join_paths(prefix, get_option('bindir')))

configure_file(
  input: app_id + '.service.in',
  output: app_id + '.service',
  configuration: dbus_conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'dbus-1/services')
)

# install_data(app_id + '.gschema.xml',
#   install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
# )

# if false
# gtk_encode_symbolic = find_program('gtk-encode-symbolic-svg')
# sizes = ['32x32', '64x64']
# icon_targets = []
# foreach size: sizes
#   icon_targets += custom_target('symbolic-icon-' + size,
#     input: 'icons/turtle-symbolic.svg',
#     output: 'turtle-symbolic.symbolic.png',
#     command: [gtk_encode_symbolic, '--output=' + meson.current_build_dir(), '@INPUT@', size]
#   )
# endforeach
# endif

icondir = join_paths(get_option('datadir'), 'icons/hicolor')
install_data('icons/org.gabmus.hydrapaper.svg',
  install_dir: join_paths(icondir, 'scalable/apps')
)
# install_data('icons/se.tingping.Trg-symbolic.svg',
#   install_dir: join_paths(icondir, 'symbolic/apps')
# )

hydrapaper_resources = gnome.compile_resources(app_id,
 app_id + '.gresource.xml',
  gresource_bundle: true,
 # dependencies: desktop_service,
 install: true,
 install_dir: pkgdatadir
)

hydrapaper_settings = gnome.compile_schemas()

install_data(
  app_id + '.appdata.xml',
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)
