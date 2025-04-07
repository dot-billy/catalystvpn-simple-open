package logger

import (
	"os"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

// InitLogger initializes the logger with the specified log level
func InitLogger(debug bool) {
	// Configure zerolog
	zerolog.TimeFieldFormat = zerolog.TimeFormatUnix
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
	if debug {
		zerolog.SetGlobalLevel(zerolog.DebugLevel)
	}

	// Pretty logging for development
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})
}

// Debug logs a debug message
func Debug(msg string, fields ...interface{}) {
	log.Debug().Fields(fields).Msg(msg)
}

// Info logs an info message
func Info(msg string, fields ...interface{}) {
	log.Info().Fields(fields).Msg(msg)
}

// Error logs an error message
func Error(msg string, err error, fields ...interface{}) {
	log.Error().Err(err).Fields(fields).Msg(msg)
}

// Fatal logs a fatal message and exits
func Fatal(msg string, err error, fields ...interface{}) {
	log.Fatal().Err(err).Fields(fields).Msg(msg)
}
