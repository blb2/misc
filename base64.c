/* An implementation of base64 encoding/decoding from RFC 1341
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHARACTERS_PER_LINE 72

typedef enum TYPE
{
	INVALID,
	ENCODE,
	DECODE
} TYPE;

static char table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

void usage_quit(void)
{
	fprintf(stderr, "Usage:\tbase64 <encode|decode> file [output]\n\n");
	fprintf(stderr, "\tencode   Use base64 encoding on file.\n");
	fprintf(stderr, "\tdecode   Use base64 decoding on file.\n");
	fprintf(stderr, "\tfile     Specifies the file to be read.  Use '-' for stdin.\n");
	fprintf(stderr, "\toutput   Specifies output file.\n\n");

	exit(EXIT_FAILURE);
}

void base64_encode(FILE* input, FILE* output)
{
	unsigned char data[3];
	unsigned char code[4];
	int done, i, ch, chcnt = 0;
	
	done = 0;
	while (!done)
	{
		data[0] = data[1] = data[2] = '\0';

		for (i = 0; i < 3; i++)
		{
			if ((ch = fgetc(input)) == -1)
			{
				done = 1;
				break;
			}

			data[i] = (unsigned char)ch;
		}

		if (i > 0)
		{
			code[0] = table[ (data[0] & 0xfc) >> 2];
			code[1] = table[((data[0] & 0x03) << 4) | ((data[1] & 0xf0) >> 4)];
			code[2] = table[((data[1] & 0x0f) << 2) | ((data[2] & 0xc0) >> 6)];
			code[3] = table[  data[2] & 0x3f];
			
			memset(code + i + 1, '=', 3 - i);
	
			for (i = 0; i < 4; i++)
				putc(code[i], output);

			chcnt += 4;

			if (chcnt >= CHARACTERS_PER_LINE)
			{
				putc('\n', output);
				chcnt = 0;
			}
		}
	}

	putc('\n', output);
}

void base64_decode(FILE* input, FILE* output)
{
	unsigned char data[3];
	unsigned int  code[4];
	int done, ch, i, j;

	done = 0;
	while (!done)
	{
		code[0] = code[1] = code[2] = code[3] = 0;

		for (i = 0; i < 4; i++)
		{
			if ((ch = fgetc(input)) == -1 || ch == '=')
			{
				done = 1;
				break;
			}

			if ('A' <= ch && ch <= 'Z')
				code[i] = ch - 'A';
			else if ('a' <= ch && ch <= 'z')
				code[i] = ch - 'a' + ('Z' - 'A' + 1);
			else if ('0' <= ch && ch <= '9')
				code[i] = ch - '0' + ('Z' - 'A' + 1) + ('z' - 'a' + 1);
			else if (ch == '+')
				code[i] = 62;
			else if (ch == '/')
				code[i] = 63;
			else
				i--;
		}

		if (i != 4 && i != 0 && ch != '=')
		{
			fprintf(stderr, "\nIncomplete input\n");
		}
		else if (i != 0)
		{
			data[0] = (unsigned char)(( code[0]         << 2) | ((code[1] & 0x30) >> 4));
			data[1] = (unsigned char)(((code[1] & 0x0F) << 4) | ((code[2] & 0x3C) >> 2));
			data[2] = (unsigned char)(((code[2] & 0x03) << 6) | code[3]);

			for (j = 0; j < i - 1; j++)
				putc(data[j], output);
		}
	}
}

int main(int argc, char* argv[])
{
	TYPE type = INVALID;
	FILE* input;
	FILE* output;

	if (argc != 3 && argc != 4)
		usage_quit();
	else if (strcmp("encode", argv[1]) == 0)
		type = ENCODE;
	else if (strcmp("decode", argv[1]) == 0)
		type = DECODE;
	else if (type == INVALID)
		usage_quit();

	output = stdout;
	
	if (strcmp(argv[2], "-") == 0)
	{
		input = stdin;
	}
	else if (!(input = fopen(argv[2], "r")))
	{
		perror(argv[2]);
		exit(EXIT_FAILURE);
	}
	else if (argc == 4 && !(output = fopen(argv[3], "w")))
	{
		perror(argv[3]);
		exit(EXIT_FAILURE);
	}

	if (type == ENCODE)
		base64_encode(input, output);
	else if (type == DECODE)
		base64_decode(input, output);

	if (input != stdin)
		fclose(input);

	if (output != stdout)
		fclose(output);
	
	return 0;
}
