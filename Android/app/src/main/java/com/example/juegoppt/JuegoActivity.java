package com.example.juegoppt;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Scanner;

public class JuegoActivity extends AppCompatActivity {

    private static final String IP_SERVIDOR = "192.168.20.8";
    private static final int    PUERTO      = 1234;

    private Socket       socket;
    private PrintWriter  salida;
    private Scanner      entrada;
    private boolean      conectado = false;

    private EditText  etNickname;
    private TextView  tvEstado, tvResultado;
    private Button    btnConfirmarNick, btnPiedra, btnPapel, btnTijera;
    private Button    btnJugarNuevo, btnVolverMenu;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_juego);

        // Referencias a la interfaz
        etNickname      = findViewById(R.id.etNickname);
        tvEstado        = findViewById(R.id.tvEstado);
        tvResultado     = findViewById(R.id.tvResultado);
        btnConfirmarNick = findViewById(R.id.btnConfirmarNick);
        btnPiedra       = findViewById(R.id.btnPiedra);
        btnPapel        = findViewById(R.id.btnPapel);
        btnTijera       = findViewById(R.id.btnTijera);
        btnJugarNuevo   = findViewById(R.id.btnJugarNuevo);
        btnVolverMenu   = findViewById(R.id.btnVolverMenu);

        // Conectar al servidor en un hilo aparte
        new Thread(() -> conectar()).start();

        // Confirmar nickname
        btnConfirmarNick.setOnClickListener(v -> {
            String nick = etNickname.getText().toString().trim();
            if (nick.isEmpty()) {
                mostrarAlerta("Aviso", "Ingresa un nickname.");
                return;
            }
            enviarMensaje("NICKNAME|" + nick);
            tvEstado.setText("Esperando al rival...");
            btnConfirmarNick.setEnabled(false);
            etNickname.setEnabled(false);
        });

        // Botones de jugada
        btnPiedra.setOnClickListener(v -> enviarJugada("piedra"));
        btnPapel.setOnClickListener(v  -> enviarJugada("papel"));
        btnTijera.setOnClickListener(v -> enviarJugada("tijera"));

        // Jugar otra vez
        btnJugarNuevo.setOnClickListener(v -> {
            tvResultado.setText("");
            tvEstado.setText("Elige tu jugada");
            btnPiedra.setEnabled(true);
            btnPapel.setEnabled(true);
            btnTijera.setEnabled(true);
            btnJugarNuevo.setEnabled(false);
        });

        // Volver al menú
        btnVolverMenu.setOnClickListener(v -> {
            enviarMensaje("cerrar");
            cerrarConexion();
            finish();
        });
    }

    private void conectar() {
        try {
            socket    = new Socket(IP_SERVIDOR, PUERTO);
            salida    = new PrintWriter(socket.getOutputStream(), true);
            entrada   = new Scanner(socket.getInputStream());
            conectado = true;
            runOnUiThread(() -> tvEstado.setText("Conectado. Ingresa tu nickname."));

            // Escuchar mensajes del servidor
            while (conectado && entrada.hasNextLine()) {
                String mensaje = entrada.nextLine();
                procesarRespuesta(mensaje);
            }
        } catch (Exception e) {
            runOnUiThread(() ->
                    mostrarAlerta("Error", "No se pudo conectar al servidor.")
            );
        }
    }

    private void procesarRespuesta(String texto) {
        String[] partes  = texto.split("\\|");
        String   comando = partes[0];

        runOnUiThread(() -> {
            switch (comando) {
                case "NICKNAME_OK":
                    tvEstado.setText("Esperando al rival...");
                    break;

                case "INICIO":
                    tvEstado.setText("¡Rival conectado! Elige tu jugada");
                    btnPiedra.setEnabled(true);
                    btnPapel.setEnabled(true);
                    btnTijera.setEnabled(true);
                    break;

                case "GANASTE":
                    tvResultado.setText("¡GANASTE! Tú: " + partes[1] + " | Rival: " + partes[2]);
                    tvResultado.setTextColor(0xFF1D9E75);
                    deshabilitarJugadas();
                    break;

                case "PERDISTE":
                    tvResultado.setText("Perdiste. Tú: " + partes[1] + " | Rival: " + partes[2]);
                    tvResultado.setTextColor(0xFFE24B4A);
                    deshabilitarJugadas();
                    break;

                case "EMPATE":
                    tvResultado.setText("¡Empate! Tú: " + partes[1] + " | Rival: " + partes[2]);
                    tvResultado.setTextColor(0xFFFF9800);
                    deshabilitarJugadas();
                    break;
            }
        });
    }

    private void enviarJugada(String jugada) {
        btnPiedra.setEnabled(false);
        btnPapel.setEnabled(false);
        btnTijera.setEnabled(false);
        tvResultado.setText("Esperando jugada del rival...");
        enviarMensaje("JUGADA|" + jugada);
    }

    private void deshabilitarJugadas() {
        btnPiedra.setEnabled(false);
        btnPapel.setEnabled(false);
        btnTijera.setEnabled(false);
        btnJugarNuevo.setEnabled(true);
    }

    private void enviarMensaje(String mensaje) {
        new Thread(() -> {
            if (salida != null) {
                salida.println(mensaje);
            }
        }).start();
    }

    private void cerrarConexion() {
        try {
            conectado = false;
            if (socket != null) socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void mostrarAlerta(String titulo, String mensaje) {
        runOnUiThread(() ->
                new AlertDialog.Builder(JuegoActivity.this)
                        .setTitle(titulo)
                        .setMessage(mensaje)
                        .setPositiveButton("OK", null)
                        .show()
        );
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        enviarMensaje("cerrar");
        cerrarConexion();
    }
}